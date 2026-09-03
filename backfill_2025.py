"""ONE-OFF BACKFILL: the FanGraphs pitch-type split tables for the 2025 season.

This is a separate, manual-only script. It reuses the helper functions in
baseball_project_data_fetcher.py but it does NOT change anything the daily
pipeline does:

  * it writes to data_2025_final/, never to data/
  * it never clears data/ and never rewrites Last_Updated.csv
  * it skips Yahoo and Savant entirely - FanGraphs splits only
  * its workflow is workflow_dispatch only, so it never runs on a schedule

Run it once from the "FanGraphs 2025 Backfill" workflow, take the CSVs, then
this file and its workflow can be deleted.
"""

import glob
import os
import shutil
import sys
import time

from selenium.webdriver.common.by import By

import baseball_project_data_fetcher as bp

SEASON = 2025
OUT_DIR = os.path.join(os.getcwd(), "data_2025_final")
os.makedirs(OUT_DIR, exist_ok=True)

# Point the shared helpers at the backfill folder. setup_driver() and
# build_fangraphs_splits_combined() both read this module global at call time,
# so overriding it here keeps every write out of data/.
bp.DOWNLOAD_DIR = OUT_DIR

# Same five tables and two handedness splits as the live pipeline, but the file
# names carry the _2025_Final suffix. build_fangraphs_splits_combined() builds
# its input paths from FG_SPLIT_HANDS and its output names from
# FG_COMBINED_NAMES, so overriding these two is all the renaming that is needed.
bp.FG_SPLIT_HANDS = {"l": "vs LHP_2025_Final", "r": "vs RHP_2025_Final"}
bp.FG_COMBINED_NAMES = {
    "l": "FanGraphs Splits Combined_vs LHP_2025_Final",
    "r": "FanGraphs Splits Combined_vs RHP_2025_Final",
}

SPLITS_TEMPLATE_2025 = bp.FG_SPLITS_TEMPLATE.replace("season=2026", f"season={SEASON}")

URLS = {}
for _hand, _hlabel in bp.FG_SPLIT_HANDS.items():
    for _sg, _tlabel in bp.FG_SPLIT_TABLES.items():
        URLS[f"FG Split_{_tlabel}_{_hlabel}"] = SPLITS_TEMPLATE_2025.format(
            hand=_hand, statgroup=_sg)

FG_EXPORT_XPATH = (
    "//*[contains(@class, 'data-export')] | "
    "//a[contains(text(), 'Export Data')] | "
    "//button[contains(text(), 'Export Data')]"
)


def main():
    print(f"FanGraphs {SEASON} backfill -> {OUT_DIR}")
    print(f"{len(URLS)} tables to download.\n")

    failed = []
    driver = bp.setup_driver()
    bp.inject_fangraphs_cookie(driver)

    for tab_name, url in URLS.items():
        print(f"\nFetching data for: {tab_name}...")
        driver.get(url)
        existing_files = set(glob.glob(os.path.join(OUT_DIR, "*.*")))

        try:
            retries = 0
            while retries < 3:
                time.sleep(4)
                if driver.find_elements(By.XPATH, "//*[contains(text(), 'Error loading data')]"):
                    print(f"  -> FanGraphs server error. Reloading (Attempt {retries + 1}/3)...")
                    driver.refresh()
                    retries += 1
                    time.sleep(3)
                else:
                    bp.safe_click(driver, FG_EXPORT_XPATH, timeout=60)
                    break

            if retries == 3:
                raise Exception("FanGraphs failed to load the data grid after 3 reloads.")

            print("  -> Exporting data...")
            latest_file = bp.wait_for_new_download(OUT_DIR, existing_files, timeout=120)

            if latest_file:
                shutil.move(latest_file, os.path.join(OUT_DIR, f"{tab_name}.csv"))
                print(f"  -> Successfully saved as: {tab_name}.csv")
            else:
                print(f"  -> WARNING: Download timed out or failed for {tab_name}!")
                failed.append(tab_name)

        except Exception as e:
            print(f"  -> Error processing {tab_name}.")
            print(f"  -> Details: {e}")
            failed.append(tab_name)

    driver.quit()

    print("\nCombining the 2025 split tables on PlayerId...")
    try:
        written = bp.build_fangraphs_splits_combined()
    except Exception as e:
        print(f"  -> Error combining splits: {e}")
        written = []

    for out_name in bp.FG_COMBINED_NAMES.values():
        if out_name not in written:
            failed.append(out_name)

    total = len(URLS) + len(bp.FG_COMBINED_NAMES)
    print("\n" + "=" * 50)
    print(f"BACKFILL SUMMARY: {total - len(failed)} of {total} outputs written.")

    if failed:
        print(f"FAILED ({len(failed)}): " + ", ".join(failed))
        print("\nNOTE: FanGraphs failures are usually an expired FANGRAPHS_COOKIE secret.")
        print("      Refresh it in Settings > Secrets and variables > Actions.")
        print("=" * 50)
        sys.exit(1)

    print(f"All {SEASON} outputs written to data_2025_final/.")
    print("=" * 50)


if __name__ == "__main__":
    main()
