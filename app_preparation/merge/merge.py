import os
import sys
import typer
import logging
import subprocess

from typing_extensions import Annotated

logger = logging.getLogger(__name__)
app = typer.Typer()

@app.command(
        name="merge",
        help="Python wrapper for APKEditor. Merge multiple APKs into a single APK. Single apks are assumed to be stored as <package_name>.apk in the apk_dir. Multiple apks are assumed to be stored in a folder named <package_name> in the apk_dir."
)
def merge(apk_dir: Annotated[str, typer.Argument(help="Directory where the APKs are stored.")], 
          package_name: Annotated[str, typer.Argument(help="Name of the package to merge.")],
          out_dir: Annotated[str, typer.Argument(help="Output directory where the merged APK will be stored.")]):
    
    if os.path.exists(os.path.join(apk_dir, f"{package_name}.apk")):
        logger.info(f"Single package {package_name} found.")
        return

    if not os.path.isdir(os.path.join(apk_dir, package_name)):
        logger.error(f"The directory '{apk_dir}' does not exist.")
        sys.exit(1)
        return
    
    merge_apk_folder = os.path.join(apk_dir, package_name)
    base_apk = os.path.join(apk_dir, f"{package_name}.apk")
    out_file = os.path.join(out_dir, f"{package_name}_merged.apk")
    
    # output should be text
    process = subprocess.Popen(
        ["java", "-jar", "APKEditor-1.4.1.jar", "m", "-i", merge_apk_folder, "-o", out_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
                               )
    stdout, stderr = process.communicate()
    # print stdout
    print(f"out: {stdout}")

    return_code = process.returncode

    if return_code != 0:
        logger.error(f"Error merging apks: {stderr}")
        sys.exit(1)
    else:
        logger.info(f"Apks merged successfully.")
        return

if __name__=="__main__":
    app()