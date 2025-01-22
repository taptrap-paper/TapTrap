import logging
import networkx as nx

from models.ApplicationInfo import ApplicationInfo
from models.ActivityInfo import ActivityInfo
from androguard.misc import AnalyzeAPK
from androguard.core.analysis.analysis import Analysis
from androguard.core.analysis.analysis import ClassAnalysis
from androguard.core.analysis.analysis import ExternalMethod
from androguard.core.dex import EncodedMethod
from androguard.core.analysis.analysis import MethodAnalysis
from androguard.core.analysis.analysis import BasicBlocks, DEXBasicBlock
from androguard.core.dex import Instruction

class CodeAnalyzer:

    # Landroid/app/Activity;
    ANIMATION_OVERRIDE_METHOD_ACTIVITY_CALLS = [
        "overridePendingTransition (I I I)V",
        "overridePendingTransition (I I)V"
    ]

    application_info: ApplicationInfo
    call_graph: nx.DiGraph
    dx: Analysis

    def __init__(self, application_info: ApplicationInfo, dx: Analysis):
        self.application_info = application_info
        self.dx = dx
        self.override_methods: list[MethodAnalysis] = []

    def analyze(self):
        logging.info(f"Analyzing code for {self.application_info.package_name}")
        self.call_graph: nx.DiGraph = self.dx.get_call_graph()
        print("Callgraph created")

        self.application_info.protected_confirmation = self.uses_android_protected_confirmation()

        self.override_methods = self.get_override_methods()
        
        for m in self.override_methods:
            # For debugging purposes, we store all invocations of animation override methods
            m: MethodAnalysis
            xrefs: list[tuple[ClassAnalysis, MethodAnalysis, int]] = m.get_xref_from()
            for xref in xrefs:
                xref_method: MethodAnalysis = xref[1]
                self.application_info.override_animation_calls.append(xref_method.full_name)

        for activity_info in self.application_info.activities:
            class_analysis = self.get_activity_class_analysis_for_activity(activity_info)
            if class_analysis == None:
                self.application_info.not_found_activities.append(activity_info.activity_name)
                print(f"Could not find class analysis for activity {activity_info.activity_name}")
            else:
                entry_method: ExternalMethod = self.create_entry_method(class_analysis)
                self.check_on_enter_animation_override(class_analysis, activity_info)
                self.check_animation_override_method(entry_method, activity_info)

    
    def check_animation_override_method(self, entry_method: ExternalMethod | EncodedMethod, activity_info: ActivityInfo):
        for m in self.override_methods:
            m: MethodAnalysis
            if nx.has_path(self.call_graph, source = entry_method, target = m.get_method()):
                all_paths = nx.all_simple_paths(self.call_graph, source=entry_method, target=m.get_method(), cutoff=10)
                if (self.check_paths(all_paths)):
                    activity_info.animation_override_methods.append(m.full_name)
    

    def get_activity_class_analysis_for_activity(self, activity_info: ActivityInfo) -> ClassAnalysis:
        raw_name = activity_info.activity_name
        if activity_info.is_alias:
            raw_name = activity_info.alias_for

        # we have to change the notation from . to / and add the L and ;
        activity_class_name = f"L{raw_name.replace('.', '/')};"

        activity_class = self.dx.get_class_analysis(activity_class_name)
        return activity_class
    
    
    def check_on_enter_animation_override(self, class_analysis, activity_info: ActivityInfo) -> None:
        """
        Check if the activity overrides the onEnterAnimationComplete method
        """
        current_superclass: ClassAnalysis = class_analysis
            
        while current_superclass.name != "Landroid/app/Activity;" and current_superclass.name != "Ljava/lang/Object;":
            for m in current_superclass.get_methods():
                if "onEnterAnimationComplete ()V" in m.full_name:
                    if (m.is_external()):
                        # we ignore external methods as they are not part of the APK
                        pass
                    else:
                        activity_info.overrides_on_enter_animation_complete = True
                        activity_info.on_enter_animation_override = f"{current_superclass.name}\n{m.get_method().get_source()}"
                        return
            current_superclass_name = current_superclass.extends
            current_superclass = self.dx.get_class_analysis(current_superclass_name)

    def get_last_method_in_hierarchy(self, class_analysis: ClassAnalysis, method_name: str):
        current_superclass: ClassAnalysis = class_analysis
        while current_superclass.name != "Ljava/lang/Object;":
            for m in current_superclass.get_methods():
                if method_name in m.full_name:
                    return m.get_method()
            current_superclass_name = current_superclass.extends
            current_superclass = self.dx.get_class_analysis(current_superclass_name)
        raise Exception(f"Could not find method {method_name} in class hierarchy")
    


    def is_class_subclass_of(self,  class_name: str, superclass: str):
        class_analysis: ClassAnalysis = self.dx.get_class_analysis(class_name)
        current_superclass: ClassAnalysis = class_analysis
        
        while current_superclass.name != "Ljava/lang/Object;":
            if (current_superclass.name == superclass):
                return True
            current_superclass_name = current_superclass.extends
            current_superclass = self.dx.get_class_analysis(current_superclass_name)
        
        return False


    def get_override_methods(self) -> list[MethodAnalysis]:
        override_methods: list[MethodAnalysis] = []

        for c in self.dx.get_classes():
            for method_analysis in c.get_methods():
                encoded_method: EncodedMethod = method_analysis.get_method()
                full_name: str = method_analysis.full_name

                if any([x in full_name for x in CodeAnalyzer.ANIMATION_OVERRIDE_METHOD_ACTIVITY_CALLS]):
                    class_name = encoded_method.get_class_name()
                    if (self.is_class_subclass_of(class_name, "Landroid/app/Activity;")):
                        override_methods.append(method_analysis)

        return override_methods
    

    def create_entry_method(self, class_analysis: ClassAnalysis) -> ExternalMethod:
        # get all lifecycle methods of this class, i.e., methods that start with 'on' and are defined in application classes
        lifecycle_methods: list[MethodAnalysis] = []
        current_superclass: ClassAnalysis = class_analysis
        
        while current_superclass.name != "Landroid/app/Activity;" and current_superclass.name != "Ljava/lang/Object;":
            for m in current_superclass.get_methods():
                if m.name.startswith("on"):
                    # check if there is already a method with the same name and parameters
                    # If so, we ignore it, as it is an override
                    name_with_params = m.name + m.get_method().get_descriptor()
                    if not any([x.name + x.get_method().get_descriptor() == name_with_params for x in lifecycle_methods]):
                        lifecycle_methods.append(m)

            current_superclass_name = current_superclass.extends
            current_superclass = self.dx.get_class_analysis(current_superclass_name)

        # create a new dummy method that calls all lifecycle methods
        # this is necessary to have a single entry point for the analysis
        class_name = class_analysis.name
        class_name = class_name.replace("/", "_")
        class_name = class_name.replace(";", "")
        class_name = class_name[1:]

        dummy_name = f"{class_name}_dummy"
        entry_method: ExternalMethod = ExternalMethod("DummyClass", dummy_name, "()V")
        self.call_graph.add_node(entry_method)
        for m in lifecycle_methods:
            m: MethodAnalysis
            self.call_graph.add_edge(entry_method, m.get_method())
        
        return entry_method
    
    def check_paths(self, paths: list[list]) -> bool:
        for path in paths:
            result = self.check_path(path)
            print(f"Checked path {path} with result {result}")
            if result:
                print(f"Path {path} is ok")
                return True
        return False


    def check_path(self, path: list):


        # check if 'finish' is on the path. If it is, we ignore it
        if any([x.name == "finish" for x in path]):
            return False

            
        print("----")
        for i in range(len(path) - 2, 0, -1):
            current_analysis_method: MethodAnalysis = self.dx.get_method_analysis(path[i])
            next_analysis_method: MethodAnalysis = self.dx.get_method_analysis(path[i+1])
                
            print(f"Checking {current_analysis_method.full_name} -> {next_analysis_method.full_name}")

            # Find the calls to the next method and saved them in the target list. this is a tuple of the block and the instruction where the call happens
            target: tuple[DEXBasicBlock, Instruction] = []

            for block in current_analysis_method.get_basic_blocks().get():
                block: DEXBasicBlock
                for ins in block.get_instructions():
                    # Check if the instruction is a method invocation
                    if ins.get_name().startswith("invoke"):
                        ins: Instruction
                        sig = next_analysis_method.class_name + "->" + next_analysis_method.name + next_analysis_method.descriptor
                        if sig in str(ins):
                            target.append((block, ins))
                
            is_ok = False
                
            for b, i in target:
                b: DEXBasicBlock
                i: Instruction

                visited_blocks = set()
                stack = [(b, i)]

                while stack:
                    block, ins = stack.pop()
                    if block.get_name() in visited_blocks:
                        continue

                    visited_blocks.add(block.get_name())
                    instructions = list(block.get_instructions())

                    start = True
                    if i != None:
                        start = False
                        
                    bad_call_found = False
                    for ins in reversed(instructions):
                        # Wait until we reach the instruction that we care about to check anything
                        if ins == i:
                            start = True
                        if not start:
                            continue
                            
                        if (self.is_start_activity_instruction(ins)):
                            bad_call_found = True
                            break

                        
                    if not bad_call_found:
                        preds = list(block.get_prev())
                        print(f"Preds: {preds}")
                        if len(preds) == 0:
                            # we are at the beginning of the method
                            is_ok = True
                            continue
                        for _, _, pred_block in preds:
                            print(f"Adding {pred_block}")
                            stack.append((pred_block, None))

            if not is_ok:
                return False
                

        return True

    def is_start_activity_instruction(self, ins):
        inst_str = str(ins)
        if ("startActivity" in inst_str) or ("finish" in inst_str):
            return True
        return False
    

    def uses_android_protected_confirmation(self) -> bool:
        """
        Checks if the application uses Android Protected Confirmation.
        """
        # We check if the app calls the ConfirmationPrompt.presentPrompt method.
        # This is the method that is used to launch the protected confirmation dialog.
        for c in self.dx.get_classes():
            if c.name == "Landroid/security/ConfirmationPrompt;":
                for m in c.get_methods():
                    if m.name == "presentPrompt":
                        return True
        return False