CREATE STAGE IF NOT EXISTS WHISPER_APP ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') DIRECTORY = (ENABLE = TRUE);

CREATE STAGE IF NOT EXISTS AUDIO_FILES ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') DIRECTORY = (ENABLE = TRUE);

CREATE STAGE IF NOT EXISTS SPECS ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') DIRECTORY = (ENABLE = TRUE);

CREATE COMPUTE POOL PR_GPU_3
MIN_NODES = 1 
MAX_NODES = 1 
INSTANCE_FAMILY = GPU_NV_S 
AUTO_RESUME = FALSE;

ALTER compute pool PR_GPU_3 RESUME;

-- Upload the whisper_spec.yml to @specs stage before creating the service
CREATE SERVICE Whisper_Audio_text_SVC
  IN COMPUTE POOL PR_GPU_3
  FROM @specs
  SPEC='whisper_spec.yml'
  MIN_INSTANCES=1
  MAX_INSTANCES=1;

--Check the status of the service
SELECT SYSTEM$GET_SERVICE_STATUS('Whisper_Audio_text_SVC',1);

-- Check the log for the service
SELECT value AS log_line
FROM TABLE(
 SPLIT_TO_TABLE(SYSTEM$GET_SERVICE_LOGS('Whisper_Audio_text_SVC', 0, 'audio-whisper-app'), '\n')
  );

/*
Below queries are creating the service function
 */

 -- Function to get duration of the audio files
CREATE OR REPLACE FUNCTION DURATION(AUDIO_FILE TEXT)
RETURNS VARIANT
SERVICE=Whisper_Audio_text_SVC
ENDPOINT=API
AS '/audio-duration';

-- Function to detect language from audio file
CREATE OR REPLACE FUNCTION DETECT_LANGUAGE(AUDIO_FILE TEXT, ENCODE BOOLEAN)
RETURNS VARIANT
SERVICE=Whisper_Audio_text_SVC
ENDPOINT=API
AS '/detect-language';

-- Function to transcribe audio files
CREATE OR REPLACE FUNCTION TRANSCRIBE(TASK TEXT, LANGUAGE TEXT, AUDIO_FILE TEXT, ENCODE BOOLEAN)
RETURNS VARIANT
SERVICE=Whisper_Audio_text_SVC
ENDPOINT=API
AS '/asr';

CREATE or REPLACE TABLE ALL_CLAIMS_RAW (
	DATETIME DATE,
	AUDIOFILE VARCHAR(16777216),
	CONVERSATION VARCHAR(16777216),
	PRESIGNED_URL_PATH VARCHAR(16777216),
	DURATION FLOAT NOT NULL
);

/*
If you don't have the audio files and want to play with the demo then run load the audio_sample.csv file
into the table created above. You can use PUT or Snowsight to load the csv to the above created table(ALL_CLAIMS_RAW)
 */ 




/*

Run the below command only if you have audio files.

INSERT INTO ALL_CLAIMS_RAW
(
DATETIME,
AUDIOFILE,
PRESIGNED_URL_PATH,
CONVERSATION,
DURATION
)
SELECT CAST(CASE WHEN split(RELATIVE_PATH,'/')[1]::string IS NULL THEN GETDATE() 
            ELSE split(RELATIVE_PATH,'/')[0]::string END AS DATE) as Datetime, 
        CASE WHEN split(RELATIVE_PATH,'/')[1]::string is null then split(RELATIVE_PATH,'/')[0]::string 
            ELSE split(RELATIVE_PATH,'/')[1]::string END as RELATIVE_PATH,
       GET_PRESIGNED_URL('@AUDIO_FILES', RELATIVE_PATH) AS PRESIGNED_URL
       -- ,DETECT_LANGUAGE(PRESIGNED_URL,TRUE) as DETECT_LANGUAGE
       ,TRANSCRIBE('transcribe','',PRESIGNED_URL,True)['text']::string AS EXTRACTED_TEXT
       ,DURATION(PRESIGNED_URL):call_duration_seconds::DOUBLE as CALL_DURATION_SECONDS
FROM DIRECTORY('@AUDIO_FILES');

 */



