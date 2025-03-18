# Changelog

### Changed on 2024-12-04
- **File Renaming**
  - Renamed `.gitignore` file:
    - `libs/garmin_fpl-0.5.0/.gitignore` → `libs/garmin_fpl/.gitignore`
  - Renamed Python scripts (without changes):
    - `libs/garmin_fpl-0.5.0/03_BBox_creator.py` → `libs/garmin_fpl/BBox_creator_03.py`
    - `libs/garmin_fpl-0.5.0/02_CombineWPT.py` → `libs/garmin_fpl/CombineWPT_02.py`
    - `libs/garmin_fpl-0.5.0/20230704_DEC2DMM.py` → `libs/garmin_fpl/DEC2DMM_20230704.py`
    - `libs/garmin_fpl-0.5.0/20230704_WPnameChanger.py` → `libs/garmin_fpl/WPnameChanger_20230704.py`
    - `libs/garmin_fpl-0.5.0/01_create_gfp_from_userwpt.py` → `libs/garmin_fpl/create_gfp_from_userwpt_01.py`
    - `libs/garmin_fpl-0.5.0/04_track_from_userwpt.py` → `libs/garmin_fpl/track_from_userwpt_04.py`
    - `libs/garmin_fpl-0.5.0/20230704_wpt_to_gfp.py` → `libs/garmin_fpl/wpt_to_gfp_20230704.py`
  - Renamed additional files:
    - `libs/garmin_fpl-0.5.0/CITATION.cff` → `libs/garmin_fpl/CITATION.cff`
    - `libs/garmin_fpl-0.5.0/LICENSE.md` → `libs/garmin_fpl/LICENSE.md`
    - `libs/garmin_fpl-0.5.0/README.md` → `libs/garmin_fpl/README.md`

- **Modifications**
  - Added `libs/garmin_fpl/__init__.py` to convert directory to python package.
  - `libs/garmin_fpl-0.5.0/01_create_gfp_from_userwpt.py`:
    - Modified script references inside the file to reflect the new filenames.
    - Example:  
      ```python
      os.system(f'python 20230704_WPnameChanger.py {target}_user.wpt')
      ```
      was changed to:
      ```python
      os.system(f'python WPnameChanger_20230704.py {target}_user.wpt')
      ```
  
- **Example Project Files Renamed** (no content changes):
  - `libs/garmin_fpl-0.5.0/example_project/052_DeltaNorthHF_01_1000m_fpl.gfp` → `libs/garmin_fpl/example_project/052_DeltaNorthHF_01_1000m_fpl.gfp`
  - `libs/garmin_fpl-0.5.0/example_project/052_DeltaNorthHF_01_1000m_user.wpt` → `libs/garmin_fpl/example_project/052_DeltaNorthHF_01_1000m_user.wpt`
  - `libs/garmin_fpl-0.5.0/example_project/052_DeltaNorthHF_01_1000m_user_renamed.wpt` → `libs/garmin_fpl/example_project/052_DeltaNorthHF_01_1000m_user_renamed.wpt`
  - `libs/garmin_fpl-0.5.0/example_project/052_DeltaNorthHF_01_1000m_user_renamed_BBox.txt` → `libs/garmin_fpl/example_project/052_DeltaNorthHF_01_1000m_user_renamed_BBox.txt`
  - `libs/garmin_fpl-0.5.0/example_project/052_DeltaNorthHF_01_1000m_user_renamed_DMM.wpt` → `libs/garmin_fpl/example_project/052_DeltaNorthHF_01_1000m_user_renamed_DMM.wpt`

- **Figure Files Renamed**:
  - `libs/garmin_fpl-0.5.0/figs/garmin_gtn750_screen_grid-fpl.png` → `libs/garmin_fpl/figs/garmin_gtn750_screen_grid-fpl.png`
  - `libs/garmin_fpl-0.5.0/figs/macs-missionplanner_052.png` → `libs/garmin_fpl/figs/macs-missionplanner_052.png`

### Changed on 2024-12-29
- **Modifications**
  - `libs/garmin_fpl/DEC2DMM_20230704.py`:
    - Added target param to dec2ddm_pandas

### Changed on 2025-01-21
- **Modifications**
  - `libs/garmin_fpl/DEC2DMM_20230704.py`:
    - Rewrote dec2ddm function without dependencies on numpy and pandas