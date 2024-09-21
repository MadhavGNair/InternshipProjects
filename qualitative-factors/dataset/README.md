# Dataset

This folder contains all the datasets used for the project.

The folder structure and files are explained below,

## ./synthetic_data_generation
This folder contains the code used to generate synthetic dataset using the atomic factors. Refer to the README within the folder for details and instructions on how to generate synthetic data.

## ./synthetic_data
This folder contains the generate synthetic data. Each file is named using the following pattern: syn_data_vX_DDMMYY, where,

- X - version number (higher = newer)
- DDMMYY - date format of when the data was generated

The dataset itself has the following format,

[{
&emsp;"text" : (str) the generated text,
&emsp;"main_topic": (str) the main topic,
&emsp;"main_ground_truth": (Dict) the questions relating to main topic,
&emsp;"leak_topic": (str) the leak topic,
&emsp;"leak_ground_truth" : (Dict) the questions relating to leak topic,
&emsp;"ground_truth": (List) all the questions as a list,
&emsp;"input_tokens": (int) number of input tokens,
&emsp;"output_tokens": (int) number of output tokens
}]

The [main/leak]_ground_truth dictionary must follow the format:

{
"main_topic": {
&emsp;"sub_topic_1": [list of questions],
&emsp;...,
&emsp;}
"leak_topic": None or Dict in the same format as main_topic
}