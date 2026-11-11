Local evaluation environment: Windows. Your working directory is D:\omniALE\ALE_repro\runs\video_storyboard_001\attempt_002. Python with Pillow, NumPy, SciPy, OpenCV and python-docx is on PATH; FFmpeg and ffprobe are on PATH. Use input/ only as supplied; use work/ for scratch and output/ for deliverables. Complete the task autonomously and save the requested artifact. Only access this task working directory and installed runtime tools. Do not search the web for this benchmark task, access other runs, inspect evaluation code, or read reference answers. No evaluator feedback is available during the run. The official task description follows; only absolute file paths have been localized.

## Context

A small restoration studio is about to begin a scan + remaster pass on a public-domain print of a vintage Yasuji Murata animation. Before any restoration work starts, the pipeline requires an **archival shot log / continuity report** of the source print: a temporal, per-shot factual record of what is on screen, written by an archival assistant editor.

The QC team has handed you a **restoration fact-check brief** (a list of factual visual questions about the film). Your shot log must preserve enough detail that downstream QC engineers can verify every item in the brief by reading the log alone. As the archivist, you record facts — you do **not** answer the brief's questions or insert interpretation. Answering is the QC engineers' job.

## Input Files
- Source print: `D:\omniALE\ALE_repro\runs\video_storyboard_001\attempt_002\input\Yasuji_Murata-_A_Wolf_is_a_Wolf_(1931).ogv`
- QC fact-check brief: `D:\omniALE\ALE_repro\runs\video_storyboard_001\attempt_002\input\video_storyboard_qa_set.docx`

## Software
- Use any DOCX-capable workflow available on the VM.
- A task-local launcher is available at: `D:\omniALE\ALE_repro\runs\video_storyboard_001\attempt_002\software\launch_word_processor.cmd`

## Your Task
1. Inspect the full source print end-to-end.
2. Read the QC brief so the log preserves the facts each item in the brief depends on.
3. Produce a concise, complete shot log in temporal order.
4. Organize the log as shots or segments. Each shot or segment must include:
   - shot or segment ID
   - start time and end time
   - brief visual description
   - key actions or events
   - important objects, people, animals, and scene details
   - visible on-screen text or dialogue relevant to the brief
5. Do **not** answer the brief's questions in the log. Record only the observable facts a QC engineer would need to answer them.
6. Use only information grounded in the source print. Do not add external knowledge, plot context, or interpretation.

## Output
- Save the final readable Word document exactly here: `D:\omniALE\ALE_repro\runs\video_storyboard_001\attempt_002\output\storyboard.docx`
- The output file must be a valid `.docx` file named `storyboard.docx`.
