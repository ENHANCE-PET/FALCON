## 🙋‍♂️ FAQ

### Q1: Permission error on shared resource Windows systems

**Example error message:**

​```
ERROR [file_utilities.py:65] Could not set permissions for \falcon-windows-x86_64\greedy.exe on Windows
​```

or

​```
File "\Anaconda\lib\runpy.py", line 197, in _run_module_as_main
return _run_code(code, main_globals, None,
File "\Anaconda\lib\runpy.py", line 87, in run_code
exec(code, run_globals)
File "\Falcon\falconz_env\Scripts\falconz.exe_main.py", line 7, in
File "\Falcon\falconz_env\lib\site-packages\falconz\falconz.py", line 214, in main
start_frame_file = determine_candidate_frames(candidate_frames, reference_file, falcon_dir, actual_n_jobs)
File "\falconz_env\lib\site-packages\falconz\image_processing.py", line 441, in determine_candidate_frames
return candidate_files[candidate_frames[0]]
IndexError: list index out of range
​```

**Solution:**

1. In `\{your falcon env}\Lib\site-packages\falconz\file_utilities.py`, change line 58 from:
   ​```
   subprocess.check_call(["icacls", file_path, "/grant", "Everyone:(F)"])
   ​```
   to:
   ​```
   pass
   ​```

2. If it still doesn't work, add the `\{your falcon env}\bin\falcon-windows-x86_64` directory to your PATH environment variable:
   - In Search, search for and select: "System (Control Panel)"
   - Click on the "Advanced system settings" link
   - Click on "Environment Variables"
   - In the "System Variables" section, find the "PATH" environment variable and select it
   - Click on "Edit"
   - Add the `\{your falcon env}\bin\falcon-windows-x86_64` directory to the list of paths
   - Click "OK" to save the changes