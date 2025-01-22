import pandas as pd
import click
import os
import json

RESULT = {}

@click.command()
@click.option("--result_dir", required=True, help="Path to the result directory.")
def main(result_dir: str):
    result_df = get_result_df(result_dir)

    result_df = check_failed_timeout(result_dir, result_df)
    df_apps = app_level_results(result_df)
    df_activities = activity_level_results(result_df)

    summary(df_apps, df_activities)

    printLatex()


def get_result_df(result_dir):
    result_files = [f for f in os.listdir(os.path.join(result_dir, "output")) if f.endswith('.json')]
    parsed_json_files = []
    for json_file in result_files:
        with open(os.path.join(result_dir, "output", json_file), 'r') as f:
            parsed_json_files.append(json.load(f))

    df = pd.json_normalize(parsed_json_files)
    return df

def check_failed_timeout(result_dir, df):
    df_metrics = df.copy()
    joblog_path = os.path.join(result_dir, "logs", "joblog.log")
    joblog_df = pd.read_csv(joblog_path, sep='\t')
    if 'Exitval' not in joblog_df.columns:
        raise ValueError("The joblog does not contain the 'Exitval' column.")
    failed_count = joblog_df[joblog_df["Exitval"] != 0].shape[0]
    timeout_count = joblog_df[joblog_df["Exitval"] == 124].shape[0]
    success_count = joblog_df[joblog_df["Exitval"] == 0].shape[0]
    total_count = joblog_df.shape[0]
    print(f"- Total number of apps (according to joblog): {total_count}")
    print(f"- Apps timed out (according to joblog): {timeout_count} ({timeout_count/total_count*100:.2f}%)")

    n_success = len(df_metrics[df_metrics['exception'] == False])

    
    print(f"- Apps succeeded (according to joblog): {success_count} ({success_count/total_count*100:.2f}%)")
    print(f"- Apps succeeded (according to results): {n_success}")
    
    if (n_success != success_count):
        print("! There is a mismatch between the number of successful apps in the joblog and the number of successful apps in the results.")


    # get all package names where joblog is successful
    successful_packages_joblog = joblog_df[joblog_df["Exitval"] == 0]["Command"].tolist()
    successful_packages_joblog = [x.split("free_18_12_24_merged/")[1] for x in successful_packages_joblog]
    successful_packages_joblog = [x.split("_merged.apk ")[0] for x in successful_packages_joblog]
    successful_packages_joblog = [x.split(".apk ")[0] for x in successful_packages_joblog]

    # get all package names where the results are successful
    successful_packages_results = df_metrics[df_metrics['exception'] == False]["package_name"].tolist()

    # get the difference between the two lists
    difference = list(set(successful_packages_joblog) - set(successful_packages_results))
    print(f"- Number of apps where the results are successful but the joblog is not: {len(difference)}")
    print(difference)


    RESULT["vulntapAppsSuccess"] = f"{success_count:,}"
    RESULT["vulntapAppsSuccessPercent"] = f"{success_count/total_count*100:.2f}"
    RESULT["vulntapAppsTimeout"] = f"{timeout_count:,}"


    df_metrics['duration'] = (df_metrics['end_time'] - df_metrics['start_time'])
    avg_duration = df_metrics['duration'].mean()

    RESULT["vulntapAvgDuration"] = f"{round(avg_duration)}"
    return df_metrics[df_metrics['exception'] == False]


def app_level_results(df):
    df_apps = df.copy()
    n_apps = len(df_apps)
    df_apps['n_activities'] = df_apps['activities'].apply(lambda x: len(x))
    print(f"- Min number of activities: {df_apps['n_activities'].min()}")
    print(f"- Max number of activities: {df_apps['n_activities'].max()}")
    print(f"- Average number of activities: {df_apps['n_activities'].mean()}")

    n_enabled_apps = len(df_apps[df_apps['is_enabled'] == True])
    print(f"- Number of enabled apps: {n_enabled_apps} ({n_enabled_apps/n_apps*100:.2f}%)")

    n_no_permission = len(df_apps[df_apps['permission'].apply(lambda x: x == None)])
    print(f"- Number of apps with no required permission: {n_no_permission} ({n_no_permission/n_apps*100:.2f}%)")

    df_apps["launchable"] = (df_apps["is_enabled"] == True) & (df_apps["permission"].apply(lambda x: x is None))
    n_launchable = len(df_apps[df_apps["launchable"] == True])
    print(f"- Number of launchable apps: {n_launchable} ({n_launchable/n_apps*100:.2f}%)")

    n_apc = len(df_apps[df_apps['protected_confirmation'] == True])
    print(f"- Number of apps that use Android Protected Confirmation: {n_apc} ({n_apc/n_apps*100:.2f}%)")
    
    RESULT["vulntapProtectedConfirmationApps"] = f"{n_apc}"
    RESULT["vulntapProtectedConfirmationAppsPercent"] = f"{n_apc/n_apps*100:.2f}"

    return df_apps


def activity_level_results(df):
    # Explode the activities column
    df_activities = df.copy()
    df_activities = df_activities[['package_name', 'activities']]
    # get the ones that actually have activities
    df_activities = df_activities[df_activities['activities'].apply(lambda x: len(x) > 0)]

    df_activities = df_activities.explode('activities')

    activities_normalized = pd.json_normalize(df_activities['activities'], max_level=0)

    # Combine back with packageName
    df_activities = df_activities.drop(columns=['activities']).reset_index(drop=True)
    df_activities = pd.concat([df_activities, activities_normalized], axis=1)


    n_total_activities = len(df_activities)
    print(f"- Total number of activities: {n_total_activities}")
    RESULT["vulntapAmountActivities"] = f"{n_total_activities:,}"

    n_exported_activities = len(df_activities[df_activities['is_exported'] == True])
    print(f"- Number of exported activities: {n_exported_activities} ({n_exported_activities/n_total_activities*100:.2f}%)")
    RESULT["vulntapAmountActivitiesExported"] = f"{n_exported_activities:,}"
    RESULT["vulntapAmountActivitiesExportedPercent"] = f"{n_exported_activities/n_total_activities*100:.2f}"

    n_no_permission_activities = len(df_activities[df_activities['permission'].apply(lambda x: x is None)])
    print(f"- Number of activities with no required permission: {n_no_permission_activities} ({n_no_permission_activities/n_total_activities*100:.2f}%)")
    RESULT["vulntapAmountActivitiesNoPermission"] = f"{n_no_permission_activities:,}"
    RESULT["vulntapAmountActivitiesNoPermissionPercent"] = f"{n_no_permission_activities/n_total_activities*100:.2f}"

    n_enabled_activities = len(df_activities[df_activities['is_enabled'] == True])
    print(f"- Number of enabled activities: {n_enabled_activities} ({n_enabled_activities/n_total_activities*100:.2f}%)")
    RESULT["vulntapAmountActivitiesEnabled"] = f"{n_enabled_activities:,}"
    RESULT["vulntapAmountActivitiesEnabledPercent"] = f"{n_enabled_activities/n_total_activities*100:.2f}"

    df_activities["launchable"] = (df_activities["is_exported"] == True) & (df_activities["is_enabled"] == True) & (df_activities["permission"].apply(lambda x: x is None))
    n_launchable_activities = len(df_activities[df_activities["launchable"] == True])
    print(f"- Number of launchable activities: {n_launchable_activities} ({n_launchable_activities/n_total_activities*100:.2f}%)")
    RESULT["vulntapAmountActivitiesLaunchable"] = f"{n_launchable_activities:,}"
    RESULT["vulntapAmountActivitiesLaunchablePercent"] = f"{n_launchable_activities/n_total_activities*100:.2f}"

    df_activities["same_task"] = df_activities["launch_mode"].apply(lambda x: x == "singleTop" or x == "standard")
    n_same_task_activities = len(df_activities[df_activities["same_task"] == True])
    print(f"- Number of activities with launch mode 'singleTop' or 'standard': {n_same_task_activities} ({n_same_task_activities/n_total_activities*100:.2f}%)")
    RESULT["vulntapAmountActivitiesSameTask"] = f"{n_same_task_activities:,}"
    RESULT["vulntapAmountActivitiesSameTaskPercent"] = f"{n_same_task_activities/n_total_activities*100:.2f}"

    n_overrides_onenteranimationcomplete = len(df_activities[df_activities["overrides_on_enter_animation_complete"] == True])
    print(f"- Number of activities that override onEnterAnimation: {n_overrides_onenteranimationcomplete} ({n_overrides_onenteranimationcomplete/n_total_activities*100:.2f}%)")
    RESULT["vulntapAmountActivitiesNoAnimationFinishWait"] = f"{n_overrides_onenteranimationcomplete:,}"
    RESULT["vulntapAmountActivitiesNoAnimationFinishWaitPercent"] = f"{n_overrides_onenteranimationcomplete/n_total_activities*100:.2f}"

    n_unique_content_in_onenteranimationcomplete = len(df_activities["on_enter_animation_override"].unique()) - 1 # to ignore 'null'
    print(f"- Number of unique content in onEnterAnimation: {n_unique_content_in_onenteranimationcomplete}")

    # check if the array is empty or not
    df_activities["restrict_animation"] = df_activities["animation_override_methods"].apply(lambda x: len(x) > 0)
    activities_use_override_pending_transition = df_activities["animation_override_methods"].apply(lambda x: len(x) > 0)
    n_activities_use_override_pending_transition = len(df_activities[activities_use_override_pending_transition])
    print(f"- Number of activities that use overridePendingTransition: {n_activities_use_override_pending_transition} ({n_activities_use_override_pending_transition/n_total_activities*100:.2f}%)")
    RESULT["vulntapAmountActivitiesAnimationRestriction"] = f"{n_activities_use_override_pending_transition:,}"
    RESULT["vulntapAmountActivitiesAnimationRestrictionPercent"] = f"{n_activities_use_override_pending_transition/n_total_activities*100:.2f}"


    # check if the activity is vulnerable
    df_activities["vulnerable"] = df_activities["launchable"] & df_activities["same_task"] & ~df_activities["restrict_animation"] & ~df_activities["overrides_on_enter_animation_complete"]
    n_vulnerable_activities = len(df_activities[df_activities["vulnerable"] == True])
    print(f"- Number of vulnerable activities: {n_vulnerable_activities} ({n_vulnerable_activities/n_total_activities*100:.2f}%)")
    RESULT["vulntapAmountActivitiesVulnerable"] = f"{n_vulnerable_activities:,}"
    RESULT["vulntapAmountActivitiesVulnerablePercent"] = f"{n_vulnerable_activities/n_total_activities*100:.2f}"

    return df_activities


def summary(df_apps, df_activities):
    n_apps = len(df_apps["package_name"].unique())
    
    # get the amount of apps that have at least one activity that is externally launchable
    df_activities_exported = df_activities[df_activities["launchable"] == True]
    df_activities_exported = df_activities_exported.groupby("package_name").filter(lambda x: len(x) > 0)
    n_apps_multiple_exported_activities = len(df_activities_exported["package_name"].unique())
    print(f"- Number of apps with more than one launchable activity: {n_apps_multiple_exported_activities}")
    RESULT["vulntapAmountAppsMinOneActivityLaunchable"] = f"{n_apps_multiple_exported_activities:,}"
    RESULT["vulntapAmountAppsMinOneActivityLaunchablePercent"] = f"{n_apps_multiple_exported_activities/n_apps*100:.2f}"

    # get the amount of apps that have at least one activity that is launchable same-task
    df_activities_same_task = df_activities[df_activities["same_task"] == True]
    df_activities_same_task = df_activities_same_task.groupby("package_name").filter(lambda x: len(x) > 0)
    n_apps_multiple_same_task_activities = len(df_activities_same_task["package_name"].unique())
    print(f"- Number of apps with more than one activity with launch mode 'singleTop' or 'standard': {n_apps_multiple_same_task_activities}")
    RESULT["vulntapAmountAppsMinOneActivitySameTask"] = f"{n_apps_multiple_same_task_activities:,}"
    RESULT["vulntapAmountAppsMinOneActivitySameTaskPercent"] = f"{n_apps_multiple_same_task_activities/n_apps*100:.2f}"

    # get the amount of apps that have at least one activity that restricts animations
    df_activities_no_animation_finish_wait = df_activities[df_activities["restrict_animation"] == True]
    df_activities_no_animation_finish_wait = df_activities_no_animation_finish_wait.groupby("package_name").filter(lambda x: len(x) > 0)
    n_apps_multiple_no_animation_finish_wait_activities = len(df_activities_no_animation_finish_wait["package_name"].unique())
    print(f"- Number of apps with more than one activity that restricts animations: {n_apps_multiple_no_animation_finish_wait_activities}")
    RESULT["vulntapAmountAppsMinOneActivityRestrictAnimation"] = f"{n_apps_multiple_no_animation_finish_wait_activities:,}"
    RESULT["vulntapAmountAppsMinOneActivityRestrictAnimationPercent"] = f"{n_apps_multiple_no_animation_finish_wait_activities/n_apps*100:.2f}"

    # get the amount of apps that wait for the animation to finish
    df_activities_no_animation_finish_wait = df_activities[df_activities["overrides_on_enter_animation_complete"] == True]
    df_activities_no_animation_finish_wait = df_activities_no_animation_finish_wait.groupby("package_name").filter(lambda x: len(x) > 0)
    n_apps_multiple_no_animation_finish_wait_activities = len(df_activities_no_animation_finish_wait["package_name"].unique())
    print(f"- Number of apps with more than one activity that waits for the animation to finish: {n_apps_multiple_no_animation_finish_wait_activities}")
    RESULT["vulntapAmountAppsMinOneActivityWaitAnimationFinish"] = f"{n_apps_multiple_no_animation_finish_wait_activities:,}"
    RESULT["vulntapAmountAppsMinOneActivityWaitAnimationFinishPercent"] = f"{n_apps_multiple_no_animation_finish_wait_activities/n_apps*100:.2f}"

    # number of apps that have at least one activity that is vulnerable
    df_activities_vulnerable = df_activities[df_activities["vulnerable"] == True]
    df_activities_vulnerable = df_activities_vulnerable.groupby("package_name").filter(lambda x: len(x) > 0)
    n_apps_multiple_vulnerable_activities = len(df_activities_vulnerable["package_name"].unique())
    print(f"- Number of apps with more than one vulnerable activity: {n_apps_multiple_vulnerable_activities}")
    RESULT["vulntapAmountAppsMinOneActivityVulnerable"] = f"{n_apps_multiple_vulnerable_activities:,}"
    RESULT["vulntapAmountAppsMinOneActivityVulnerablePercent"] = f"{n_apps_multiple_vulnerable_activities/n_apps*100:.2f}"


def printLatex():
    print("\n\n\n")
    for key, value in RESULT.items():
        print(f"\\newcommand{{\{key}}}{{{value}}}")

if __name__ == '__main__':
    main()