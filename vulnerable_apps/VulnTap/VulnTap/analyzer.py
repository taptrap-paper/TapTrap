import sys
import time
import click
import logging
from androguard.misc import AnalyzeAPK
from loguru import logger

from models.ApplicationInfo import ApplicationInfo

from ManifestAnalyzer import ManifestAnalyzer
from CodeAnalyzer import CodeAnalyzer
from ResultAggregator import ResultAggregator

logger.remove()
logger.add(sys.stderr, level="WARNING")

@click.command()
@click.option("-apk", help="Path to the APK file", required=True)
@click.option("-output", help="Output directory", required=True, default="./results")
def main(apk: str, output: str):
    print(f"Analyzing {apk}")
    application_info: ApplicationInfo = ApplicationInfo(apk_path=apk)
    application_info.start_time = time.time()
    try:
        a, _, dx = AnalyzeAPK(apk)
        print("Analyzed APK")
        ManifestAnalyzer(application_info, a).analyze()
        CodeAnalyzer(application_info, dx).analyze()
    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        application_info.end_time = time.time()
        application_info.exception = True
        ResultAggregator().write_to_file(output, application_info)
        raise e

    application_info.end_time = time.time()
    ResultAggregator().write_to_file(output, application_info)
    logging.info(f"Analysis successfully finished in {application_info.end_time - application_info.start_time} seconds")

if __name__ == '__main__':
    main()