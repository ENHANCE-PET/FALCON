
## 🧐 Frequently Asked Questions (FAQ)


### Q1: How to Resolve Permission Errors on Shared Resources in Windows Systems (Contribution

**Problem Description:**

Users may encounter permission errors when attempting to execute certain files on Windows systems. These errors typically prevent the proper setting of permissions or the execution of specific scripts within the Falcon environment. Common error messages include:

```
ERROR [file_utilities.py:65] Could not set permissions for \falcon-windows-x86_64\greedy.exe on Windows
```

or

```
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
```

**Solution:**

To resolve permission errors on Windows, follow the steps below:

1. **Modify Permission Settings in the Falcon Environment:**

   Locate the file `file_utilities.py` within your Falcon environment, typically found at `\{your falcon env}\Lib\site-packages\falconz\`.

   Change the following line (line 58 as an example):
   ```
   subprocess.check_call(["icacls", file_path, "/grant", "Everyone:(F)"])
   ```
   To simply:
   ```
   pass
   ```

   This step bypasses the attempt to explicitly set file permissions, which may not be necessary depending on your system's configuration and security policies.

2. **Update System PATH Environment Variable:**

   If the above solution does not resolve the issue, ensure that the Falcon executable directory is included in your system's PATH environment variable.

   - Navigate to the Control Panel and open System settings.
   - Select "Advanced system settings" and then click on "Environment Variables".
   - Under "System Variables", locate and select the "PATH" variable, then click on "Edit".
   - Append the directory path `\{your falcon env}\bin\falcon-windows-x86_64` to the list of existing paths.
   - Confirm all dialogs by clicking "OK" to apply the changes.

Following these steps should resolve any permission-related errors encountered within the Falcon environment on Windows systems. If issues persist, consider reviewing your system's security policies or contacting support for further assistance.
