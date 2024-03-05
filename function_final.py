import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# Function to predict ramdom question's answer (new function)
def predict_responses_randon_qa(answer):
    
    df = pd.read_csv('answer.csv')
    # Drop the 'name' column as it's not used for similarity calculation
    df = df.drop('name', axis=1)
    # Convert categorical responses to numerical values
    df = df.replace({'yes': 1, 'no': 0})

    # getting the dictionary and removing the column name
    answer.pop('name', None)
    # getting the list of index that the answer is given
    answer_index = list(answer.keys())
    # getting the list of answered question and not answered question
    X = df[answer_index]
    y = df.drop(columns=answer_index)

    # converting answer to 1/0
    new_user_responses = {key : 1 if value == 'yes' else 0 for key,value in answer.items()}
    # converting the response to dataframe
    new_user_df = pd.DataFrame([new_user_responses])
    # Compute cosine similarity between the new user and existing users
    similarities = cosine_similarity(new_user_df, X)
    # Find the indices that would sort the array in descending order
    sorted_indices = np.argsort(similarities[0])[::-1]
    #sorting the values in desending order where max similarity is in front
    # Sort the similarities array based on the sorted indices
    sorted_similarities = similarities[0, sorted_indices]
    # taking top 5 users and getting the prediction value from top 5 most similar below
    top_5_list = sorted_indices[:5]
    # getting the top 5 values from the dataframe using index and making dataframe 
    op_df = pd.DataFrame()
    for i in top_5_list:
        values_to_append = df.loc[i,list(y.keys())].values
        op_df = pd.concat([op_df , pd.DataFrame(data = [values_to_append] ,columns = list(y.keys()) )] , ignore_index=True)
    output = {}
    for col in list(y.keys()):
        val = op_df.loc[: ,col].mode()[0]
        mod_val = "yes" if val == 1 else "no"
        output.update({col : mod_val})
    return output



# Function to predict q21 to q25 for a new user based on cosine similarity

def predict_responses(new_user_responses):

    # Load your dataset
    # Assuming your dataset is in a CSV file named 'responses.csv'
    df = pd.read_csv('answer.csv')

    # Drop the 'name' column as it's not used for similarity calculation
    df = df.drop('name', axis=1)

    # Convert categorical responses to numerical values
    df = df.replace({'yes': 1, 'no': 0})

    # Use q1 to q20 for both features (X)
    X = df.iloc[:, :20]  # Features q1 to q20
    y = df.iloc[:, 20:26]  # Features q1 to q20
    
    # Convert new user responses to numerical values
    new_user_responses = [1 if response.lower() == 'yes' else 0 for response in new_user_responses]

    # Compute cosine similarity between the new user and existing users
    similarities = cosine_similarity([new_user_responses], X)

    # Find the indices that would sort the array in descending order
    sorted_indices = np.argsort(similarities[0])[::-1]
    
    #sorting the values in desending order where max similarity is in front
    # Sort the similarities array based on the sorted indices
    sorted_similarities = similarities[0, sorted_indices]

    # taking top 5 users and getting the prediction value from top 5 most similar below
    top_5_list = sorted_indices[:5]
    # getting the top 5 values from the dataframe using index and making dataframe 
    op_df = pd.DataFrame()
    for i in top_5_list:
        values_to_append = df.iloc[i, 20:].values
        op_df = pd.concat([op_df , pd.DataFrame([values_to_append])] , ignore_index=True)

    q1 = op_df.iloc[:, 0].mode()[0]
    q2 = op_df.iloc[:, 1].mode()[0]
    q3 = op_df.iloc[:, 2].mode()[0]
    q4 = op_df.iloc[:, 3].mode()[0]
    q5 = op_df.iloc[:, 4].mode()[0]

    return [q1 , q2 , q3 , q4 , q5]