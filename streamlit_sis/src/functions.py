from snowflake.snowpark.session import Session
import snowflake.snowpark.functions as F
def get_dates(session:Session):
    # Getting unique dates 
    date_list=[data[0] for data in session.table('Audio_Claims_Extracted_info').select('DATETIME').sort(F.col("DATETIME"), ascending=True).distinct().collect()]
    date_list.sort()
    st_dt,ed_dt=date_list[0],date_list[-1]
    
    return (st_dt,ed_dt)

def extract_audio_info(s_date,e_date):
    return f"""
                select 
                    datetime,
                    concat(cast(year(datetime) as string),'-',monthname(datetime)) as year_month,
                    round(duration/60) duration,
                    call_details:Representative::string as representative_name,
                    call_details:Customer::string as customer_name,
                    IFF(call_sentiment>0.7,'Positive','Negative') as call_sentiment,
                    call_details:CallIntent::string as call_intent,
                    call_summary,
                    call_details:ClaimNumber::string as claim_number ,
                    call_details:PolicyNumber::string as policy_number,
                    call_details:CallToAction::string as call_to_action,
                    call_details:PurposeOfCall::string as purpose_of_call,
                    call_details:Issue::string as issue,
                    call_details:Resolution::string as resolution,
                    call_details:ResponseMode::string as response_mode,
                    call_details:ModeofUpdate::string as update_mode,
                    IFF(call_details:FirstCallResolution>0.5,'Yes','No') as first_call_resolution,
                    audio_file_name as filename,
                    audio_full_file_path as filepath
                    
                from Audio_Claims_Extracted_info  where datetime>= '{s_date}' and datetime<= '{e_date}';
    """
def get_agent_call_stats(s_date,e_date):
    return f"""
                select 
                    datetime,
                    call_details:ClaimNumber::string as claim_number ,
                    call_details:PolicyNumber::string as policy_number,
                    call_details:Representative::string as representative_name,
                    call_details:Customer::string as customer_name,
                    call_details:CallIntent::string as call_intent,
                    call_details:Summary::string as call_summary,
                    call_details:Sentiment::string as call_sentiment_json,
                    call_sentiment,
                    audio_full_file_path as filepath
                from Audio_Claims_Extracted_info datetime>= '{s_date}' and datetime<= '{e_date}'
    """
def get_topic_info(s_date,e_date):
        return f''' 
                    select count(*) as value , topic as name
                    from
                    (
                    select 
                                    --    'Demo' as topic
                                       SNOWFLAKE.CORTEX.COMPLETE(
                                           'llama2-70b-chat',
                                               CONCAT('What is the topic of the conversation in 2 words. Example Insurance Claim or Policy Claims. Do not  paraphase and do not include the prompt and the questions in the output also no summary included. Only output the answer', raw_conversation)
                                       )   as topic                 
                                    from Audio_Claims_Extracted_info  where datetime>= '{s_date}' and datetime<= '{e_date}'
                                    ) z group by name;

                '''
def get_call_intent(s_date,e_date):
        return f'''
                    select count(*) as value , call_details:CallIntent::string as name
                    from              
                                     Audio_Claims_Extracted_info where datetime>= '{s_date}' and datetime<= '{e_date}'
                                     group by name
                '''
    
def get_call_aggregation(s_date,e_date):
    return f'''
            select count(*) as TotalCalls ,sum(duration) as TotalCallDuration
            from              
                             Audio_Claims_Extracted_info where datetime>= '{s_date}' and datetime<= '{e_date}'
                             group by name
        '''

def get_agent_call_duration(s_date,e_date):
      return f'''
                    select avg(duration)/60 total_duration_mins ,call_details:Representative::string as Agent  
                    from Audio_Claims_Extracted_info 
                    where datetime>= '{s_date}' and datetime<= '{e_date}'
                    group by Agent
                '''

def get_sentiment_ratio(s_date,e_date):
      return f'''
                select 
                    --concat(CAST(year(datetime) AS string),'-',monthname(datetime),'-',week(datetime)) as YearMonthWeek, 
                    concat(CAST(year(datetime) AS string),'-',monthname(datetime)) as YearMonth,
                    count(*) as total_sentiment_count,
                    COUNT(CASE WHEN IFF(call_sentiment>0.7,1,0) = 1 THEN 1 END) AS positive_sentiment_count,
                    total_sentiment_count-positive_sentiment_count as negative_sentiment_count,
                    round((positive_sentiment_count/total_sentiment_count)*100,2) as postive_ratio, round((1-(positive_sentiment_count/total_sentiment_count))*100,2) as negative_ratio                
                from Audio_Claims_Extracted_info
                where datetime>= '{s_date}' and datetime<= '{e_date}'
                group by YearMonth
                order by YearMonth
                '''

def get_ratio():
      return f'''
                select 
                    --concat(CAST(year(datetime) AS string),'-',monthname(datetime),'-',week(datetime)) as YearMonthWeek, 
                    concat(CAST(year(datetime) AS string),'-',monthname(datetime)) as YearMonth,
                    count(*) as total_sentiment_count,
                    COUNT(CASE WHEN IFF(call_sentiment>0.7,1,0) = 1 THEN 1 END) AS positive_sentiment_count,
                    total_sentiment_count-positive_sentiment_count as negative_sentiment_count,
                    round((positive_sentiment_count/total_sentiment_count)*100,2) as postive_ratio, round((1-(positive_sentiment_count/total_sentiment_count))*100,2) as negative_ratio                
                from Audio_Claims_Extracted_info
                group by YearMonth
                order by YearMonth
                '''

# -- where datetime>= '{s_date}' and datetime<= '{e_date}'


def mode(row):
   if row['UPDATE_MODE'] == 'Phone':
      return 'Phone'
   if row['UPDATE_MODE'] == 'Phone call':
      return 'Phone'
   if row['UPDATE_MODE'] == 'Email':
      return 'Email'
   return 'Other'