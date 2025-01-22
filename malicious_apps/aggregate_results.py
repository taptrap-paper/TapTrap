import pandas as pd
import sqlite3
import click
import os

RESULT = {}


@click.command()
@click.option("--result_dir", required=True, help="Path to the result directory.")
def main(result_dir: str):
    extract_check_failed(result_dir)
    
    db = open_db(result_dir)
    
    extract_number_animations(db)
    extract_number_unique_animations(db)
    extract_number_unique_interpolators(db)

    analyze_number_animations_failed(db)
    analyze_alpha_score_min(db)
    analyze_scale_score_min(db)
    analyze_score_min_apps(db)
    analyze_unique_animations_extended_duration(db)



    printLatex()


def open_db(result_dir: str):
    # open the sqlite database
    db_path = os.path.join(result_dir, "db.sqlite")
    con = sqlite3.connect(db_path)
    return con.cursor()

# Extraction

def extract_check_failed(result_dir: str):
    try:
        joblog_path = os.path.join(result_dir, "logs", "joblog.log")
        joblog_df = pd.read_csv(joblog_path, sep='\t')
        if 'Exitval' not in joblog_df.columns:
            raise ValueError("The joblog does not contain the 'Exitval' column.")
        failed_count = joblog_df[joblog_df["Exitval"] != 0].shape[0]
        
        print(f"- Extraction failed for apps: {failed_count}")
        success_count = joblog_df[joblog_df["Exitval"] == 0].shape[0]
        RESULT["maltapNumberSuccessApps"] = f"{success_count:,}"
        percent = (100*(success_count / (success_count + failed_count)))
        RESULT["maltapNumberSuccessAppsPercent"] = f"{percent:.2f}"
    except Exception as e:
        print(f"x Exception during extraction of failed apps")


def extract_number_animations(db):
    query = "SELECT COUNT(*) AS unique_count FROM (SELECT DISTINCT package_name, file_name FROM anim)"
    number_animations = db.execute(query).fetchone()[0]
    RESULT["maltapNumberAnimations"] = f"{number_animations:,}"
    print(f"- Number of animations: {number_animations}")

def extract_number_unique_animations(db):
    query = "SELECT COUNT(DISTINCT hash) FROM anim"
    number_unique_animations = db.execute(query).fetchone()[0]
    RESULT["maltapNumberUniqueAnimations"] = f"{number_unique_animations:,}"
    print(f"- Number of unique animations: {number_unique_animations}")

def extract_number_unique_interpolators(db):
    query = "SELECT COUNT(DISTINCT hash) FROM interpolator WHERE package_name != 'framework-res'"
    number_unique_interpolators = db.execute(query).fetchone()[0]
    print(f"- Number of unique custom interpolators: {number_unique_interpolators}")



# Analyze

def analyze_number_animations_failed(db):
    query = "SELECT COUNT(*) FROM score WHERE alpha_score < 0"
    number_animations_failed = db.execute(query).fetchone()[0]
    RESULT["maltapNumberAnimationsFailed"] = f"{number_animations_failed:,}"
    print(f"- Number of animations with failed analysis: {number_animations_failed}")

def analyze_alpha_score_min(db):
    query = "SELECT DISTINCT anim.package_name FROM score JOIN anim ON score.hash = anim.hash WHERE alpha_score >= 50"
    alpha_score_min = db.execute(query).fetchall()
    RESULT["maltapNumberAppsAlphaScoreMin"] = f"{len(alpha_score_min):,}"
    print(f"- Number of apps with alpha score >= 50: {len(alpha_score_min)}")

def analyze_scale_score_min(db):
    query = "SELECT DISTINCT anim.package_name FROM score JOIN anim ON score.hash = anim.hash WHERE scale_score >= 50"
    scale_score_min = db.execute(query).fetchall()
    RESULT["maltapNumberAppsScaleScoreMin"] = f"{len(scale_score_min):,}"
    print(f"- Number of apps with scale score >= 50: {len(scale_score_min)}")

def analyze_score_min_apps(db):
    query = "SELECT DISTINCT anim.package_name FROM score JOIN anim ON score.hash = anim.hash WHERE alpha_score >= 50 OR scale_score >= 50"
    score_min_apps = db.execute(query).fetchall()
    RESULT["maltapNumberAppsAnimationsScoreMin"] = f"{len(score_min_apps):,}"
    print(f"- Number of apps with at least one animation with score >= 50: {len(score_min_apps)}")

def analyze_unique_animations_extended_duration(db):
    query = "SELECT COUNT(DISTINCT hash) FROM score WHERE animation_longer == 1"
    unique_animations_extended_duration = db.execute(query).fetchone()[0]
    RESULT["maltapNumberUniqueAnimationsExtendedDuration"] = f"{unique_animations_extended_duration:,}"
    print(f"- Number of unique animations with extended duration: {unique_animations_extended_duration}")


def printLatex():
    print("\n\n\n")
    for key, value in RESULT.items():
        print(f"\\newcommand{{\{key}}}{{{value}}}")


if __name__ == '__main__':
    main()