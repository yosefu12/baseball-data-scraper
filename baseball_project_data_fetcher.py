import time
import os
import glob
import shutil
import io
import re
import requests
import pandas as pd
from datetime import datetime
import zoneinfo # Added zoneinfo to handle timezone conversion
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. CONFIGURATION: FOLDERS (CLOUD VERSION) ---
# We use the current working directory of the GitHub Linux server instead of your Mac's hard drive
DOWNLOAD_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --- 2. CONFIGURATION: YOUR EXACT LINKS ---
URLS_TO_DOWNLOAD = {
    "FanGraphs Hitter Data": "https://www.fangraphs.com/leaders/major-league?pos=all&stats=bat&lg=all&season=2026&season1=2026&ind=0&v_cr=202301&qual=1&type=c%2C0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C12%2C13%2C14%2C15%2C16%2C17%2C18%2C19%2C20%2C21%2C22%2C23%2C24%2C25%2C26%2C27%2C28%2C29%2C30%2C31%2C32%2C33%2C34%2C35%2C36%2C37%2C38%2C39%2C40%2C41%2C42%2C43%2C44%2C45%2C46%2C47%2C48%2C49%2C50%2C51%2C52%2C53%2C54%2C55%2C56%2C57%2C58%2C59%2C60%2C61%2C62%2C65%2C66%2C67%2C68%2C69%2C70%2C71%2C73%2C74%2C75%2C76%2C77%2C78%2C79%2C80%2C81%2C82%2C83%2C84%2C85%2C86%2C87%2C88%2C89%2C90%2C91%2C92%2C93%2C94%2C95%2C96%2C97%2C98%2C99%2C100%2C101%2C102%2C103%2C104%2C105%2C106%2C107%2C108%2C109%2C110%2C111%2C112%2C113%2C114%2C115%2C116%2C117%2C118%2C119%2C120%2C121%2C122%2C123%2C124%2C125%2C126%2C127%2C128%2C129%2C130%2C131%2C132%2C133%2C134%2C135%2C136%2C137%2C138%2C139%2C140%2C141%2C142%2C143%2C144%2C145%2C146%2C147%2C148%2C149%2C150%2C151%2C152%2C153%2C154%2C155%2C156%2C157%2C158%2C159%2C160%2C161%2C162%2C163%2C164%2C165%2C166%2C167%2C168%2C169%2C170%2C171%2C172%2C173%2C174%2C175%2C176%2C177%2C178%2C179%2C180%2C181%2C182%2C183%2C184%2C185%2C186%2C187%2C188%2C189%2C190%2C191%2C192%2C193%2C194%2C195%2C196%2C197%2C198%2C199%2C200%2C201%2C202%2C203%2C204%2C205%2C206%2C207%2C208%2C209%2C210%2C211%2C212%2C213%2C214%2C215%2C216%2C217%2C218%2C219%2C220%2C221%2C222%2C223%2C224%2C225%2C226%2C227%2C228%2C229%2C230%2C231%2C232%2C233%2C234%2C235%2C236%2C237%2C238%2C239%2C240%2C241%2C242%2C243%2C244%2C245%2C246%2C247%2C248%2C249%2C250%2C251%2C252%2C253%2C254%2C255%2C256%2C257%2C258%2C259%2C260%2C261%2C262%2C263%2C264%2C265%2C266%2C267%2C268%2C269%2C270%2C271%2C272%2C273%2C274%2C275%2C276%2C277%2C278%2C279%2C280%2C281%2C282%2C283%2C284%2C285%2C286%2C287%2C288%2C289%2C290%2C291%2C292%2C293%2C294%2C295%2C296%2C297%2C298%2C299%2C300%2C301%2C302%2C303%2C304%2C305%2C306%2C307%2C308%2C309%2C310%2C311%2C312%2C313%2C314%2C315%2C316%2C317%2C318%2C319%2C320%2C321%2C322%2C323%2C324%2C325%2C326%2C327%2C328%2C329%2C330%2C331%2C332%2C333%2C334%2C335%2C336%2C337%2C338%2C339%2C340%2C341%2C342%2C343%2C344%2C345%2C346%2C347%2C348%2C349%2C350%2C351%2C352%2C353%2C354%2C355%2C356%2C357%2C358%2C359%2C360%2C361%2C362%2C363%2C364%2C365%2C366%2C367%2C368%2C369%2C370%2C371%2C372%2C373%2C374%2C375%2C376%2C377%2C378%2C379%2C380%2C381%2C382%2C383%2C384%2C385%2C386%2C387%2C388%2C389%2C390%2C391%2C392%2C393%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C402%2C403%2C404%2C405%2C406%2C407%2C408%2C409%2C410%2C411%2C412%2C413%2C414%2C415%2C416%2C417%2C418%2C419%2C420%2C421%2C422%2C423%2C424%2C425%2C426%2C427%2C428%2C429%2C430%2C431%2C432%2C433%2C434%2C435%2C436%2C437%2C438%2C439%2C440%2C441%2C442%2C443%2C444%2C445%2C446%2C447%2C448%2C449%2C450%2C451%2C452%2C453%2C454%2C455%2C456%2C457%2C458&month=0",
    "FanGraphs Pitcher Data": "https://www.fangraphs.com/leaders/major-league?pos=all&stats=pit&lg=all&type=c%2C-1%2C0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C12%2C13%2C14%2C15%2C16%2C17%2C18%2C19%2C20%2C21%2C22%2C23%2C24%2C25%2C26%2C27%2C28%2C29%2C30%2C31%2C32%2C33%2C34%2C35%2C36%2C37%2C38%2C39%2C40%2C41%2C42%2C43%2C44%2C45%2C46%2C47%2C48%2C49%2C50%2C51%2C52%2C53%2C54%2C55%2C56%2C57%2C58%2C59%2C60%2C61%2C62%2C63%2C64%2C65%2C66%2C67%2C68%2C69%2C70%2C71%2C72%2C73%2C74%2C75%2C76%2C77%2C78%2C79%2C80%2C81%2C82%2C83%2C84%2C85%2C86%2C87%2C88%2C89%2C90%2C91%2C92%2C93%2C94%2C95%2C96%2C97%2C98%2C99%2C100%2C101%2C102%2C103%2C104%2C105%2C106%2C107%2C108%2C109%2C110%2C111%2C112%2C113%2C114%2C115%2C116%2C117%2C118%2C119%2C120%2C121%2C122%2C123%2C124%2C125%2C126%2C127%2C128%2C129%2C130%2C131%2C132%2C133%2C134%2C135%2C136%2C137%2C138%2C139%2C140%2C141%2C142%2C143%2C144%2C145%2C146%2C147%2C148%2C149%2C150%2C151%2C152%2C153%2C154%2C155%2C156%2C157%2C158%2C159%2C160%2C161%2C162%2C163%2C164%2C165%2C166%2C167%2C168%2C169%2C170%2C171%2C172%2C173%2C174%2C175%2C176%2C177%2C178%2C179%2C180%2C181%2C182%2C183%2C184%2C185%2C186%2C187%2C188%2C189%2C190%2C191%2C192%2C193%2C194%2C195%2C196%2C197%2C198%2C199%2C200%2C201%2C202%2C203%2C204%2C205%2C206%2C207%2C208%2C209%2C210%2C211%2C212%2C213%2C214%2C215%2C216%2C217%2C218%2C219%2C220%2C221%2C222%2C223%2C224%2C225%2C226%2C227%2C228%2C229%2C230%2C231%2C232%2C233%2C234%2C235%2C236%2C237%2C238%2C239%2C240%2C241%2C242%2C243%2C244%2C245%2C246%2C247%2C248%2C249%2C250%2C251%2C252%2C253%2C254%2C255%2C256%2C257%2C258%2C259%2C260%2C261%2C262%2C263%2C264%2C265%2C266%2C267%2C268%2C269%2C270%2C271%2C272%2C273%2C274%2C275%2C276%2C277%2C278%2C279%2C280%2C281%2C282%2C283%2C284%2C285%2C286%2C287%2C288%2C289%2C290%2C291%2C292%2C293%2C294%2C295%2C296%2C297%2C298%2C299%2C300%2C301%2C302%2C303%2C304%2C305%2C306%2C307%2C308%2C309%2C310%2C311%2C312%2C313%2C314%2C315%2C316%2C317%2C319%2C319%2C320%2C321%2C322%2C323%2C324%2C325%2C326%2C327%2C328%2C329%2C330%2C331%2C332%2C333%2C334%2C335%2C336%2C337%2C338%2C339%2C340%2C341%2C342%2C343%2C344%2C345%2C346%2C347%2C348%2C349%2C350%2C351%2C352%2C353%2C354%2C355%2C356%2C357%2C358%2C359%2C360%2C361%2C362%2C363%2C364%2C365%2C366%2C367%2C368%2C369%2C370%2C371%2C372%2C373%2C374%2C375%2C376%2C377%2C378%2C379%2C380%2C381%2C382%2C383%2C384%2C385%2C386%2C387%2C388%2C389%2C390%2C391%2C392%2C393%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C402%2C403%2C404%2C405%2C406%2C407%2C408%2C409%2C410%2C411%2C412%2C413%2C414%2C415%2C416%2C417%2C418%2C419%2C420%2C421%2C422%2C423%2C424%2C425%2C426%2C427%2C428%2C429%2C430%2C431%2C432%2C433%2C434%2C435%2C436%2C437%2C438%2C439%2C440%2C441%2C442%2C443%2C444%2C445%2C446%2C447%2C448%2C449%2C450%2C451%2C452%2C453%2C454%2C455%2C456%2C457%2C458%2C459%2C460%2C461%2C462%2C463%2C464%2C465%2C466%2C467%2C468%2C469%2C470%2C471%2C472%2C473%2C474%2C475%2C476%2C477%2C478%2C479%2C480%2C481%2C482%2C483%2C484%2C485%2C486%2C487%2C488%2C489%2C490%2C491%2C492%2C493%2C494%2C495%2C496%2C497%2C498%2C499%2C500%2C501%2C502%2C503%2C504%2C505%2C506%2C507%2C508%2C509%2C510%2C511%2C512%2C513%2C514%2C515%2C516%2C517%2C518%2C519%2C520%2C521%2C522%2C523%2C524%2C525%2C526%2C527%2C528%2C529%2C530%2C531&season=2026&month=0&season1=2026&ind=0&v_cr=202301&pageitems=2000000000&qual=0",
    "Savant_Hitters_Overall": "https://baseballsavant.mlb.com/statcast_search?hfPT=&hfAB=&hfGT=R%7C&hfPR=&hfZ=&hfStadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2026%7C&hfSit=&player_type=batter&hfOuts=&home_road=&pitcher_throws=&batter_stands=&hfSA=&hfEventOuts=&hfEventRuns=&hfABSFlag=&game_date_gt=&game_date_lt=&hfMo=&hfTeam=&hfOpponent=&hfRO=&position=&hfInfield=&hfOutfield=&hfInn=&hfBBT=&hfFlag=is%5C.%5C.bunt%5C.%5C.not%7C&metric_1=&group_by=name&min_pitches=0&min_results=0&min_pas=0&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc&chk_stats_pa=on&chk_stats_abs=on&chk_stats_bip=on&chk_stats_hits=on&chk_stats_singles=on&chk_stats_dbls=on&chk_stats_triples=on&chk_stats_hrs=on&chk_stats_so=on&chk_stats_k_percent=on&chk_stats_bb=on&chk_stats_bb_percent=on&chk_stats_hbp=on&chk_stats_whiffs=on&chk_stats_swings=on&chk_stats_api_break_z_with_gravity=on&chk_stats_api_break_x_arm=on&chk_stats_api_break_z_induced=on&chk_stats_api_break_x_batter_in=on&chk_stats_ba=on&chk_stats_xba=on&chk_stats_xbadiff=on&chk_stats_obp=on&chk_stats_xobp=on&chk_stats_xobpdiff=on&chk_stats_slg=on&chk_stats_xslg=on&chk_stats_xslgdiff=on&chk_stats_woba=on&chk_stats_xwoba=on&chk_stats_wobadiff=on&chk_stats_barrels_total=on&chk_stats_babip=on&chk_stats_iso=on&chk_stats_swing_miss_percent=on&chk_stats_delev_run_exp=on&chk_stats_delev_pitcher_run_exp=on&chk_stats_delev_batter_run_value_per_100=on&chk_stats_delev_pitcher_run_value_per_100=on&chk_stats_unadj_run_exp=on&chk_stats_unadj_pitcher_run_exp=on&chk_stats_unadj_batter_run_value_per_100=on&chk_stats_unadj_pitcher_run_value_per_100=on&chk_stats_velocity=on&chk_stats_effective_speed=on&chk_stats_spin_rate=on&chk_stats_release_pos_z=on&chk_stats_release_pos_x=on&chk_stats_release_extension=on&chk_stats_plate_x=on&chk_stats_plate_z=on&chk_stats_arm_angle=on&chk_stats_launch_speed=on&chk_stats_hyper_speed=on&chk_stats_launch_angle=on&chk_stats_bbdist=on&chk_stats_hardhit_percent=on&chk_stats_barrels_per_bbe_percent=on&chk_stats_barrels_per_pa_percent=on&chk_stats_sweetspot_speed_mph=on&chk_stats_attack_angle=on&chk_stats_swing_length=on&chk_stats_attack_direction=on&chk_stats_swing_path_tilt=on&chk_stats_rate_ideal_attack_angle=on&chk_stats_intercept_ball_minus_batter_pos_x_inches=on&chk_stats_intercept_ball_minus_batter_pos_y_inches=on#results",
    "Savant_Hitters_vs_RHP": "https://baseballsavant.mlb.com/statcast_search?hfGT=R%7C&hfSea=2026%7C&player_type=batter&pitcher_throws=R&hfFlag=is%5C.%5C.bunt%5C.%5C.not%7C&group_by=name&min_pitches=0&min_results=0&min_pas=0&sort_col=pitches&sort_order=desc&chk_stats_pa=on&chk_stats_abs=on&chk_stats_bip=on&chk_stats_hits=on&chk_stats_singles=on&chk_stats_dbls=on&chk_stats_triples=on&chk_stats_hrs=on&chk_stats_so=on&chk_stats_k_percent=on&chk_stats_bb=on&chk_stats_bb_percent=on&chk_stats_hbp=on&chk_stats_whiffs=on&chk_stats_swings=on&chk_stats_api_break_z_with_gravity=on&chk_stats_api_break_x_arm=on&chk_stats_api_break_z_induced=on&chk_stats_api_break_x_batter_in=on&chk_stats_ba=on&chk_stats_xba=on&chk_stats_xbadiff=on&chk_stats_obp=on&chk_stats_xobp=on&chk_stats_xobpdiff=on&chk_stats_slg=on&chk_stats_xslg=on&chk_stats_xslgdiff=on&chk_stats_woba=on&chk_stats_xwoba=on&chk_stats_wobadiff=on&chk_stats_barrels_total=on&chk_stats_babip=on&chk_stats_iso=on&chk_stats_swing_miss_percent=on&chk_stats_delev_run_exp=on&chk_stats_delev_pitcher_run_exp=on&chk_stats_delev_batter_run_value_per_100=on&chk_stats_delev_pitcher_run_value_per_100=on&chk_stats_unadj_run_exp=on&chk_stats_unadj_pitcher_run_exp=on&chk_stats_unadj_batter_run_value_per_100=on&chk_stats_unadj_pitcher_run_value_per_100=on&chk_stats_velocity=on&chk_stats_effective_speed=on&chk_stats_spin_rate=on&chk_stats_release_pos_z=on&chk_stats_release_pos_x=on&chk_stats_release_extension=on&chk_stats_plate_x=on&chk_stats_plate_z=on&chk_stats_arm_angle=on&chk_stats_launch_speed=on&chk_stats_hyper_speed=on&chk_stats_launch_angle=on&chk_stats_bbdist=on&chk_stats_hardhit_percent=on&chk_stats_barrels_per_bbe_percent=on&chk_stats_barrels_per_pa_percent=on&chk_stats_sweetspot_speed_mph=on&chk_stats_attack_angle=on&chk_stats_swing_length=on&chk_stats_attack_direction=on&chk_stats_swing_path_tilt=on&chk_stats_rate_ideal_attack_angle=on&chk_stats_intercept_ball_minus_batter_pos_x_inches=on&chk_stats_intercept_ball_minus_batter_pos_y_inches=on#results",
    "Savant_Hitters_vs_LHP": "https://baseballsavant.mlb.com/statcast_search?hfGT=R%7C&hfSea=2026%7C&player_type=batter&pitcher_throws=L&hfFlag=is%5C.%5C.bunt%5C.%5C.not%7C&group_by=name&min_pitches=0&min_results=0&min_pas=0&sort_col=pitches&sort_order=desc&chk_stats_pa=on&chk_stats_abs=on&chk_stats_bip=on&chk_stats_hits=on&chk_stats_singles=on&chk_stats_dbls=on&chk_stats_triples=on&chk_stats_hrs=on&chk_stats_so=on&chk_stats_k_percent=on&chk_stats_bb=on&chk_stats_bb_percent=on&chk_stats_hbp=on&chk_stats_whiffs=on&chk_stats_swings=on&chk_stats_api_break_z_with_gravity=on&chk_stats_api_break_x_arm=on&chk_stats_api_break_z_induced=on&chk_stats_api_break_x_batter_in=on&chk_stats_ba=on&chk_stats_xba=on&chk_stats_xbadiff=on&chk_stats_obp=on&chk_stats_xobp=on&chk_stats_xobpdiff=on&chk_stats_slg=on&chk_stats_xslg=on&chk_stats_xslgdiff=on&chk_stats_woba=on&chk_stats_xwoba=on&chk_stats_wobadiff=on&chk_stats_barrels_total=on&chk_stats_babip=on&chk_stats_iso=on&chk_stats_swing_miss_percent=on&chk_stats_delev_run_exp=on&chk_stats_delev_pitcher_run_exp=on&chk_stats_delev_batter_run_value_per_100=on&chk_stats_delev_pitcher_run_value_per_100=on&chk_stats_unadj_run_exp=on&chk_stats_unadj_pitcher_run_exp=on&chk_stats_unadj_batter_run_value_per_100=on&chk_stats_unadj_pitcher_run_value_per_100=on&chk_stats_velocity=on&chk_stats_effective_speed=on&chk_stats_spin_rate=on&chk_stats_release_pos_z=on&chk_stats_release_pos_x=on&chk_stats_release_extension=on&chk_stats_plate_x=on&chk_stats_plate_z=on&chk_stats_arm_angle=on&chk_stats_launch_speed=on&chk_stats_hyper_speed=on&chk_stats_launch_angle=on&chk_stats_bbdist=on&chk_stats_hardhit_percent=on&chk_stats_barrels_per_bbe_percent=on&chk_stats_barrels_per_pa_percent=on&chk_stats_sweetspot_speed_mph=on&chk_stats_attack_angle=on&chk_stats_swing_length=on&chk_stats_attack_direction=on&chk_stats_swing_path_tilt=on&chk_stats_rate_ideal_attack_angle=on&chk_stats_intercept_ball_minus_batter_pos_x_inches=on&chk_stats_intercept_ball_minus_batter_pos_y_inches=on#results",
    "Savant_BatTrack_LHP": "https://baseballsavant.mlb.com/leaderboard/bat-tracking?gameType=Regular&minSwings=1&minGroupSwings=1&pitchHand=L&seasonStart=2026&seasonEnd=2026&type=batter",
    "Savant_BatTrack_RHP": "https://baseballsavant.mlb.com/leaderboard/bat-tracking?gameType=Regular&minSwings=1&minGroupSwings=1&pitchHand=R&seasonStart=2026&seasonEnd=2026&type=batter",
    "Savant_BatTrack_All": "https://baseballsavant.mlb.com/leaderboard/bat-tracking?gameType=Regular&minSwings=1&minGroupSwings=1&seasonStart=2026&seasonEnd=2026&type=batter",
    "Savant Pitching Data_All": "https://baseballsavant.mlb.com/leaderboard/custom?year=2026&type=pitcher&filter=&min=1&selections=player_age%2Cp_game%2Cp_formatted_ip%2Cpa%2Cab%2Chit%2Csingle%2Cdouble%2Ctriple%2Chome_run%2Cstrikeout%2Cwalk%2Ck_percent%2Cbb_percent%2Cbatting_avg%2Cslg_percent%2Con_base_percent%2Con_base_plus_slg%2Cisolated_power%2Cbabip%2Cp_earned_run%2Cp_run%2Cp_save%2Cp_blown_save%2Cp_out%2Cp_win%2Cp_loss%2Cp_wild_pitch%2Cp_balk%2Cp_shutout%2Cp_era%2Cp_opp_batting_avg%2Cp_opp_on_base_avg%2Cp_total_stolen_base%2Cp_pickoff_attempt_1b%2Cp_pickoff_attempt_2b%2Cp_pickoff_attempt_3b%2Cp_pickoff_1b%2Cp_pickoff_2b%2Cp_pickoff_3b%2Cp_lob%2Cp_rbi%2Cp_quality_start%2Cp_walkoff%2Cp_run_support%2Cp_ab_scoring%2Cp_automatic_ball%2Cp_ball%2Cp_called_strike%2Cp_catcher_interf%2Cp_complete_game%2Cp_defensive_indiff%2Cp_foul%2Cp_foul_tip%2Cp_game_finished%2Cp_game_in_relief%2Cp_gnd_into_dp%2Cp_gnd_into_tp%2Cp_hit_by_pitch%2Cp_hit_fly%2Cp_hit_ground%2Cp_hit_line_drive%2Cp_hit_into_play%2Cp_hit_scoring%2Cp_hold%2Cp_intent_ball%2Cp_intent_walk%2Cp_missed_bunt%2Cp_out_fly%2Cp_out_ground%2Cp_out_line_drive%2Cp_passed_ball%2Cp_pitchout%2Cp_relief_no_out%2Cp_sac_bunt%2Cp_sac_fly%2Cp_starting_p%2Cp_swinging_strike%2Cp_unearned_run%2Cp_total_ball%2Cp_total_bases%2Cp_total_caught_stealing%2Cp_total_pickoff%2Cp_total_pickoff_attempt%2Cp_total_pickoff_error%2Cp_total_pitches%2Cp_total_sacrifices%2Cp_total_strike%2Cp_total_swinging_strike%2Cp_inh_runner%2Cp_inh_runner_scored%2Cp_beq_runner%2Cp_beq_runner_scored%2Cp_reached_on_error%2Cxba%2Cxslg%2Cwoba%2Cxwoba%2Cxobp%2Cxiso%2Cwobacon%2Cxwobacon%2Cbacon%2Cxbacon%2Cxbadiff%2Cxslgdiff%2Cwobadiff%2Cavg_swing_speed%2Cfast_swing_rate%2Cblasts_contact%2Cblasts_swing%2Csquared_up_contact%2Csquared_up_swing%2Cavg_swing_length%2Cswords%2Cattack_angle%2Cattack_direction%2Cideal_angle_rate%2Cvertical_swing_path%2Cexit_velocity_avg%2Claunch_angle_avg%2Csweet_spot_percent%2Cbarrel%2Cbarrel_batted_rate%2Csolidcontact_percent%2Cflareburner_percent%2Cpoorlyunder_percent%2Cpoorlytopped_percent%2Cpoorlyweak_percent%2Chard_hit_percent%2Cavg_best_speed%2Cavg_hyper_speed%2Cz_swing_percent%2Cz_swing_miss_percent%2Coz_swing_percent%2Coz_swing_miss_percent%2Coz_contact_percent%2Cout_zone_swing_miss%2Cout_zone_swing%2Cout_zone_percent%2Cout_zone%2Cmeatball_swing_percent%2Cmeatball_percent%2Cpitch_count_offspeed%2Cpitch_count_fastball%2Cpitch_count_breaking%2Cpitch_count%2Ciz_contact_percent%2Cin_zone_swing_miss%2Cin_zone_swing%2Cin_zone_percent%2Cin_zone%2Cedge_percent%2Cedge%2Cwhiff_percent%2Cswing_percent%2Cpull_percent%2Cstraightaway_percent%2Copposite_percent%2Cbatted_ball%2Cf_strike_percent%2Cgroundballs_percent%2Cgroundballs%2Cflyballs_percent%2Cflyballs%2Clinedrives_percent%2Clinedrives%2Cpopups_percent%2Cpopups%2Cpitch_hand%2Cn%2Carm_angle%2Cn_ff_formatted%2Cff_avg_speed%2Cff_avg_spin%2Cff_avg_break_x%2Cff_avg_break_z%2Cff_avg_break_z_induced%2Cff_avg_break%2Cff_range_speed%2Cn_sl_formatted%2Csl_avg_speed%2Csl_avg_spin%2Csl_avg_break_x%2Csl_avg_break_z%2Csl_avg_break_z_induced%2Csl_avg_break%2Csl_range_speed%2Cn_ch_formatted%2Cch_avg_speed%2Cch_avg_spin%2Cch_avg_break_x%2Cch_avg_break_z%2Cch_avg_break_z_induced%2Cch_avg_break%2Cch_range_speed%2Cn_cu_formatted%2Ccu_avg_speed%2Ccu_avg_spin%2Ccu_avg_break_x%2Ccu_avg_break_z%2Ccu_avg_break_z_induced%2Ccu_avg_break%2Ccu_range_speed%2Cn_si_formatted%2Csi_avg_speed%2Csi_avg_spin%2Csi_avg_break_x%2Csi_avg_break_z%2Csi_avg_break_z_induced%2Csi_avg_break%2Csi_range_speed%2Cn_fc_formatted%2Cfc_avg_speed%2Cfc_avg_spin%2Cfc_avg_break_x%2Cfc_avg_break_z%2Cfc_avg_break_z_induced%2Cfc_avg_break%2Cfc_range_speed%2Cn_fs_formatted%2Cfs_avg_speed%2Cfs_avg_spin%2Cfs_avg_break_x%2Cfs_avg_break_z%2Cfs_avg_break_z_induced%2Cfs_avg_break%2Cfs_range_speed%2Cn_kn_formatted%2Ckn_avg_speed%2Ckn_avg_spin%2Ckn_avg_break_x%2Ckn_avg_break_z%2Ckn_avg_break_z_induced%2Ckn_avg_break%2Ckn_range_speed%2Cn_st_formatted%2Cst_avg_speed%2Cst_avg_spin%2Cst_avg_break_x%2Cst_avg_break_z%2Cst_avg_break_z_induced%2Cst_avg_break%2Cst_range_speed%2Cn_sv_formatted%2Csv_avg_speed%2Csv_avg_spin%2Csv_avg_break_x%2Csv_avg_break_z%2Csv_avg_break_z_induced%2Csv_avg_break%2Csv_range_speed%2Cn_fo_formatted%2Cfo_avg_speed%2Cfo_avg_spin%2Cfo_avg_break_x%2Cfo_avg_break_z%2Cfo_avg_break_z_induced%2Cfo_avg_break%2Cfo_range_speed%2Cn_sc_formatted%2Csc_avg_speed%2Csc_avg_spin%2Csc_avg_break_x%2Csc_avg_break_z%2Csc_avg_break_z_induced%2Csc_avg_break%2Csc_range_speed%2Cn_fastball_formatted%2Cfastball_avg_speed%2Cfastball_avg_spin%2Cfastball_avg_break_x%2Cfastball_avg_break_z%2Cfastball_avg_break_z_induced%2Cfastball_avg_break%2Cfastball_range_speed%2Cn_breaking_formatted%2Cbreaking_avg_speed%2Cbreaking_avg_spin%2Cbreaking_avg_break_x%2Cbreaking_avg_break_z%2Cbreaking_avg_break_z_induced%2Cbreaking_avg_break%2Cbreaking_range_speed%2Cn_offspeed_formatted%2Coffspeed_avg_speed%2Coffspeed_avg_spin%2Coffspeed_avg_break_x%2Coffspeed_avg_break_z%2Coffspeed_avg_break_z_induced%2Coffspeed_avg_break%2Coffspeed_range_speed&chart=false&x=player_age&y=player_age&r=no&chartType=beeswarm&sort=xwoba&sortDir=asc"
}

# --- 3. YAHOO CONFIGURATION ---
YAHOO_HEADERS = {
    'cookie': 'tbla_id=f200d9f9-94a6-402a-9c2c-7c807488fca6-tuctd5b72db; axids=gam=y-6aBCK5ZG2uIPHx8d7vjlfPODI9qvgLxX.SVkBbidnXmpp7x2Uw---A&dv360=eS02cHVTRDFsRTJ1RkFaaWZMdHZzUlIzLl9VWlp4bVlFLmhrSURCaHNUekZhOGdOTEM4YUpXc3hCVXJNLlA5Qm1HUHI5NH5B&ydsp=y-8iYgqfFE2uIrKDZ3tU4617IQHN3X0MVox27m6aQbx2.YTztxJaLq2nukRL0CKz13cCOS~A&tbla=y-j.fSaT5G2uLB4tts_ons4WE05cJjwspXVLsRMcV0uYiLpb3rvg---A; ySID=v=1&d=7CXPiM0r8A--; _ga=GA1.1.1581520381.1779077891; thamba=2; F=d=8wVt2zo9vMP1POziYIT2lNjkZTe82g7NYW6pCXUNYjbcUEaK83AF; PH=l=en; Y=v=1&n=1famb46id26bu&l=mdcx300btsh5sjpten8tdldbm3a1csvbe4blis6i/o&p=02v000000000000&r=108&intl=us; GUC=AQEACAJqC-FqPkIjJgTK&s=AQAAAAjPC7HB&g=agqTGw; A1=d=AQABBNbwYWYCEEOsWeQg08mSHW_9E56YuasFEgEACALhC2o-atxH0iMA_eMDAAcI1vBhZp6YuasID1lCC-J6njuG3Ne2g4NggAkBBwoBCg&S=AQAAAli92qm7ehvZ-DYMGjZXtkM; A3=d=AQABBNbwYWYCEEOsWeQg08mSHW_9E56YuasFEgEACALhC2o-atxH0iMA_eMDAAcI1vBhZp6YuasID1lCC-J6njuG3Ne2g4NggAkBBwoBCg&S=AQAAAli92qm7ehvZ-DYMGjZXtkM; _ebd=bid-anecojpj63s6m&d=68a218055b407e3713e0c34023692ee7&s=bidhashk-EhWPKBbF; _ga_P9C3W3ESF1=GS2.1.s1779077893$o1$g1$t1779077906$j47$l0$h0; gpp=DBAA; gpp_sid=-1; ucs=tr=1779826160000; A1S=d=AQABBNbwYWYCEEOsWeQg08mSHW_9E56YuasFEgEACALhC2o-atxH0iMA_eMDAAcI1vBhZp6YuasID1lCC-J6njuG3Ne2g4NggAkBBwoBCg&S=AQAAAli92qm7ehvZ-DYMGjZXtkM; OTH=v=2&s=0&d=eyJraWQiOiIwIiwiYWxnIjoiUlMyNTYifQ.eyJjdSI6eyJndWlkIjoiSUlPN0s2TExZUlRYNFg1R0RQU1FaQzJUNkkiLCJwZXJzaXN0ZW50Ijp0cnVlLCJzaWQiOiJES2dIMjV0aTZiOFMifX0.R3Ne_m1ZuvjsjMqmxD9Ey8ym89sCLjBbTBGvvW91qVv062EHjynzhCUSlnJbsmHAHXqCF0bkt81UzxfmgVkGureHZvWvVeklApa8jhZDERKi8ofNu2jHPY0GgDGNNgmtkQomKqEmcoxGcjuL_Tt-hKHTEyh_Q_Lxg8ySLvA6FXM; T=af=JnRzPTE3Nzk3Mzk3NjAmcHM9QmdYeUNCTWcwM19DRmVEMXRlanF4QS0t&d=bnMBeWFob28BZwFJSU83SzZMTFlSVFg0WDVHRFBTUVpDMlQ2SQFhYwFBSWVHVm5GLgFhbAF5b3NlZnUxMjNAZ21haWwuY29tAXNjAWRlc2t0b3Bfd2ViAWZzATJ3SDBTZzFxQ3BNUgF6egFSTXBDcUJXbkgBYQFRQUUBbGF0AVJNcENxQgFudQEw&kt=EAAMQQd1y2tmR0Qrjw65rrw6w--~I&ku=FAAltwP6R.hxCvP.N35SECi57zHlBO44Cyxw9MLiBLO9VkslF0KZqQzIpghPbmt6Hafq5rpbCJ3zher1HXdDYjjlSScGM5b5juATVDT_sXxC_0h3eUjvSqxdyzAsXmOcrnPg5aJB8UCkg.zpQHRTiQoGEaL9DVOAEAFI32MI_jS9d0-~E; OTHD=g=DBC52A0FB64C88100ABF554A8FEA3985AE31C4C67D29193141FAE0B581ED13EB&s=3EA85A77DFEFBF4113439CCBA8D14571078C17C64482995596D8968778AD82FC&b=bid-anecojpj63s6m&j=us&bd=548c86cd506cfb04686fc4f713183644&gk=x1a9z-qJCjBBcc&sk=x1a9z-qJCjBBcc&bk=x1a9z-qJCjBBcc&iv=592F8C65FECAF44B9780FABF53EBC5C0&v=1&u=0; _ga_DH1EJ1SJMC=GS2.1.s1779743151$o1$g0$t1779743159$j52$l0$h0; SPTCH=d=cXrUU6p.JZc_9mOfvEqTqFrGw0OtZviF63hk_s5oMuKqHOEFsInh491lCp6xCfUpZaPvqIpQn.INDfUumw1fyKEMVHz_APvfbEYEphHKmM9QeVd1IiiL_.LY5QoETGcHbG_96Xdb5VABARNejZ_1Z8FmbDg.HX82aCQfmXBH6aXl.I_6bIur2anTTQDXhq8ZwKQp7OlMb2f9DxtWGuHeX_S8JiBpKqpzVra7cYk8uGTIjgyw1GH5JBB_NcpISGHDpVDNisAsumCUoHZqVmXehyTBokkzv1TD.Hwjx6JQn8FpG4tW9ikAJmwmYTwUlp5NBZnpsgF0JfGV3KZZcqpVaxA7GQg4yf8_bE_YMqlhBBY.QzJtdB11mzOmWqeuLbC79ZxIJD8AXwS8we1D8DoFqumRpEDF89NRhBNeWhJigGzOrn5FGr3KEs9VYik5x.05JokbLaIM.ft6akxkAWMZGHCoiEP8ESKtSGWGcNAmx5N0T_tT01QlHyQX0J38Tumfc2ceAmP53vnEAzCpcKUtEU7_uMOUVYXhc3pUkJ8FxMb05MIPgufQpcSkIPyL6_ne2RaNWtqIquJm0VTVeWtz95A4AxV8Z9fb&v=1; cmp=t=1779743362&j=0&u=1YNN; SPT=d=94oeaOgjJpfd9fcZdaMAL2NeDcf7rbD6jPdt3smvalelfr_EJf4HhSJEtWHCZcFJHysT7gz2pfKtwRGlYj8OewrbRm.CPTarhHdw6xiq1oHjcExo8b1EoOs-&v=1; SPTB=d=NKdTrPNpI5eLNx71IfjvZirQksho251xCXIh.VqtDUTJkRKj5clMFYEqE8xN3VG9MET8OQJdz1cAvdsB5byo1IgNx5XFHjJdcIbu1gvzENc-&v=1; _ga_8CSZHGJ8KX=GS2.1.s1779743165$o6$g1$t1779744764$j13$l0$h0',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def setup_driver():
    # Configure Chrome to run invisibly (headless) for GitHub Actions
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def inject_fangraphs_cookie(driver):
    """Pulls the secret cookie from GitHub and injects it into the browser."""
    raw_cookie = os.environ.get("FANGRAPHS_COOKIE")
    
    if not raw_cookie:
        print("WARNING: FANGRAPHS_COOKIE secret not found in environment!")
        return

    print("Injecting FanGraphs authentication cookies...")
    
    # Must hit the domain once before injecting cookies
    driver.get("https://www.fangraphs.com/404")
    time.sleep(2)
    
    # Split the big cookie string into individual parts for Selenium
    cookies = raw_cookie.split(';')
    for cookie in cookies:
        if '=' in cookie:
            name, value = cookie.strip().split('=', 1)
            driver.add_cookie({
                'name': name,
                'value': value,
                'domain': '.fangraphs.com'
            })
    
    print("Authentication successful. Proceeding to custom dashboards.")

def wait_for_new_download(folder, existing_files_before_click, timeout=120):
    end_time = time.time() + timeout
    while time.time() < end_time:
        current_files = set(glob.glob(os.path.join(folder, "*.*")))
        active_downloads = [f for f in current_files if f.endswith(".crdownload") or f.endswith(".tmp")]
        
        if not active_downloads:
            new_files = current_files - existing_files_before_click
            for f in new_files:
                if f.endswith(".csv"):
                    time.sleep(2) 
                    return f
        time.sleep(1)
    return None

def safe_click(driver, xpath, timeout=60):
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", element)
            return True
        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException):
            time.sleep(1)
            continue
        except Exception:
            time.sleep(1)
            continue
    raise Exception(f"Could not find or click the download button after {timeout} seconds.")

def scrape_yahoo_data(pos_code, tab_name):
    print(f"\nFetching data for: {tab_name} (Yahoo Scraper)...")
    
    all_players_data = []
    offset = 0
    max_players_to_scrape = 2500 

    while offset < max_players_to_scrape:
        print(f"  -> Fetching players {offset} to {offset + 24}...")
        url = f"https://baseball.fantasysports.yahoo.com/b1/25878/players?&pos={pos_code}&sort=AR&sdir=1&status=ALL&eteam=ALL&fteam=NONE&stat1=S_S_2026&jsenabled=1&count={offset}"
        
        response = requests.get(url, headers=YAHOO_HEADERS)
        if response.status_code != 200:
            print(f"  -> Failed to retrieve data. Status code: {response.status_code}")
            break
            
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table')
        
        if not table:
            print("  -> No data table found on this page. Stopping scrape.")
            break
            
        df = pd.read_html(io.StringIO(str(table)))[0]
        df = df.dropna(how='all')
        all_players_data.append(df)
        
        offset += 25
        time.sleep(5)

    if all_players_data:
        final_df = pd.concat(all_players_data, ignore_index=True)
        final_df = final_df.iloc[:, 2:]
        
        text_cols = final_df.select_dtypes(include=['object', 'str']).columns
        final_df[text_cols] = final_df[text_cols].replace(r'[^\x20-\x7E\xC0-\xFF]', '', regex=True)
        
        if isinstance(final_df.columns, pd.MultiIndex):
            final_df.columns = ['_'.join(str(item) for item in col if 'Unnamed' not in str(item)).strip() for col in final_df.columns.values]
        
        full_save_path = os.path.join(DOWNLOAD_DIR, f"{tab_name}.csv")
        final_df.to_csv(full_save_path, index=False)
        print(f"  -> Successfully saved as: {tab_name}.csv")
    else:
        print(f"  -> WARNING: No data was collected for {tab_name}.")

def download_and_rename():
    # Force the server to use Eastern Time
    tz_ny = zoneinfo.ZoneInfo("America/New_York")
    pull_time = datetime.now(tz_ny)
    formatted_pull_time = pull_time.strftime("%B %d, %Y at %I:%M%p").replace(' 0', ' ')

    print("Clearing out old CSVs from the download folder...")
    for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*.csv")):
        try:
            os.remove(f)
        except Exception:
            pass

    registry = []

    scrape_yahoo_data('B', 'Yahoo Batter Data')
    registry.append({'Tab Name': 'Yahoo Batter Data', 'Last Updated': formatted_pull_time})

    scrape_yahoo_data('P', 'Yahoo Pitcher Data')
    registry.append({'Tab Name': 'Yahoo Pitcher Data', 'Last Updated': formatted_pull_time})

    driver = setup_driver()
    
    # Inject the cookie immediately upon opening the browser
    inject_fangraphs_cookie(driver)

    for tab_name, url in URLS_TO_DOWNLOAD.items():
        print(f"\nFetching data for: {tab_name}...")
        driver.get(url)
        
        existing_files = set(glob.glob(os.path.join(DOWNLOAD_DIR, "*.*")))
        
        try:
            if "fangraphs" in url.lower():
                fg_xpath = (
                    "//*[contains(@class, 'data-export')] | "
                    "//a[contains(text(), 'Export Data')] | "
                    "//button[contains(text(), 'Export Data')]"
                )
                
                fg_retries = 0
                while fg_retries < 3:
                    time.sleep(4) 
                    if driver.find_elements(By.XPATH, "//*[contains(text(), 'Error loading data')]"):
                        print(f"  -> FanGraphs server error detected. Reloading page (Attempt {fg_retries + 1}/3)...")
                        driver.refresh()
                        fg_retries += 1
                        time.sleep(3) 
                    else:
                        safe_click(driver, fg_xpath, timeout=60)
                        break
                        
                if fg_retries == 3:
                    raise Exception("FanGraphs failed to load data grid after multiple reloads.")
                
            elif "baseballsavant" in url.lower():
                if "statcast_search" in url.lower():
                    savant_xpath = (
                        "//*[@id='btnCSV'] | "
                        "//*[contains(@class, 'buttons-csv')] | "
                        "//img[contains(@src, 'disk.png')]/parent::a | "
                        "//img[contains(@src, 'disk.png')] | "
                        "//*[@title='CSV' or @title='Save as CSV']"
                    )
                else:
                    savant_xpath = (
                        "//button[contains(., 'CSV') or contains(., 'Download')] | "
                        "//a[contains(., 'CSV') or contains(., 'Download')] | "
                        "//span[contains(., 'CSV') or contains(., 'Download')]"
                    )
                    
                safe_click(driver, savant_xpath, timeout=60)
            
            print("  -> Exporting data...")
            print("  -> Waiting for the download to finish (this can take up to 90s for large tables)...")
            
            latest_file = wait_for_new_download(DOWNLOAD_DIR, existing_files, timeout=120)
            
            if latest_file:
                new_file_path = os.path.join(DOWNLOAD_DIR, f"{tab_name}.csv")
                shutil.move(latest_file, new_file_path)
                
                registry.append({'Tab Name': tab_name, 'Last Updated': formatted_pull_time})
                print(f"  -> Successfully saved as: {tab_name}.csv")
            else:
                print(f"  -> WARNING: Download timed out or failed for {tab_name}!")
                
        except Exception as e:
            print(f"  -> Error processing {tab_name}. The page structure might have changed or taken too long to load.")

    driver.quit()
    
    df_registry = pd.DataFrame(registry)
    df_registry.to_csv(os.path.join(DOWNLOAD_DIR, "Last_Updated.csv"), index=False)
    print("\n  -> Generated master timestamp file: Last_Updated.csv")

if __name__ == "__main__":
    download_and_rename()
