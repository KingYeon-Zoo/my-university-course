@echo off
echo ================================================
echo     Upload All Experiment Data Files to Docker
echo ================================================
echo.

echo Uploading experiment data files to bigdata_hive container...
echo.

echo 1. Uploading JingDong project data file...
docker cp "bigdata classwork\jingdong.requests\jd.csv" bigdata_hive:/tmp/jd.csv
if %errorlevel% equ 0 (
    echo [SUCCESS] jd.csv uploaded successfully
) else (
    echo [ERROR] jd.csv upload failed
)
echo.

echo 2. Uploading Experiment 2 data file...
docker cp "exp2\word_count_test.txt" bigdata_hive:/tmp/word_count_test.txt
if %errorlevel% equ 0 (
    echo [SUCCESS] word_count_test.txt uploaded successfully
) else (
    echo [ERROR] word_count_test.txt upload failed
)
echo.

echo 3. Uploading Experiment 3 data file...
docker cp "exp3\data.txt" bigdata_hive:/tmp/experiment3_data.txt
if %errorlevel% equ 0 (
    echo [SUCCESS] Experiment 3 data uploaded successfully
) else (
    echo [ERROR] Experiment 3 data upload failed
)
echo.

echo 4. Verifying file upload results...
echo.
echo Container file list:
docker exec -it bigdata_hive ls -la /tmp/
echo.

echo 5. Previewing file contents...
echo.
echo === jd.csv first 5 lines ===
docker exec -it bigdata_hive head -5 /tmp/jd.csv
echo.
echo === word_count_test.txt first 5 lines ===
docker exec -it bigdata_hive head -5 /tmp/word_count_test.txt
echo.
echo === experiment3_data.txt first 5 lines ===
docker exec -it bigdata_hive head -5 /tmp/experiment3_data.txt
echo.

echo ================================================
echo File upload completed! Ready to start Hive experiments.
echo ================================================
pause 