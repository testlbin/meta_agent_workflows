rerank_Template ="""
You are a workflow assistant. Based on the user's query, your task is to choose the most relevant workflow to solve the user's requirement. Strictly follow the instructions provided.

### Instructions:
1. Choose the most relevant workflow and indicate its number using the <numbers></numbers> tags.
2. Analyze the user's requirement to select the most appropriate workflow.
3. The purpose of this selection is to effectively complete the task described.

### User query:
<query>
{query}
</query>

### Candidate Workflow Details:

<Candidate_1>
Workflow 1:
{workflow_1}
</Candidate_1>

<Candidate_2>
Workflow 2:
{workflow_2}
</Candidate_2>

<Candidate_3>
Workflow 3:
{workflow_3}
</Candidate_3>

<Candidate_4>
Workflow 4:
{workflow_4}
</Candidate_4>

<Candidate_5>
Workflow 5:
{workflow_5}
</Candidate_5>

### Note:
1. Please explain your choice using the <explanation></explanation> tags. For example: <explanation>This workflow is best suited to solve the user's query because it addresses all specified needs.</explanation>.
2. Provide the number of the chosen workflow and enclose it within <numbers></numbers> tags. For example: <numbers>3</numbers>.
3. Ensure that each tag appears only once in your response.

"""


rerank_Template_for_SGLang ="""

### User query:
<query>
{query}
</query>

### Candidate Workflow Details:

<Candidate_1>
Workflow 1:
{workflow_1}
</Candidate_1>

<Candidate_2>
Workflow 2:
{workflow_2}
</Candidate_2>

<Candidate_3>
Workflow 3:
{workflow_3}
</Candidate_3>

<Candidate_4>
Workflow 4:
{workflow_4}
</Candidate_4>

<Candidate_5>
Workflow 5:
{workflow_5}
</Candidate_5>

### Note:
1. Please explain your choice using the <explanation></explanation> tags. For example: <explanation>This workflow is best suited to solve the user's query because it addresses all specified needs.</explanation>.
2. Provide the number of the chosen workflow and enclose it within <numbers></numbers> tags. For example: <numbers>3</numbers>.
3. Ensure that each tag appears only once in your response.

"""


rerank_Template_for_SGLang_top10 ="""
You are a workflow assistant. Based on the user's query, your task is to choose the most relevant workflow to solve the user's requirement. Strictly follow the instructions provided.

### Instructions:
1. Choose the most relevant workflow and indicate its number using the <numbers></numbers> tags.
2. Analyze the user's requirement to select the most appropriate workflow.
3. The purpose of this selection is to effectively complete the task described.


### User query:
<query>
{query}
</query>

### Candidate Workflow Details:

<Candidate_1>
Workflow 1:
{workflow_1}
</Candidate_1>

<Candidate_2>
Workflow 2:
{workflow_2}
</Candidate_2>

<Candidate_3>
Workflow 3:
{workflow_3}
</Candidate_3>

<Candidate_4>
Workflow 4:
{workflow_4}
</Candidate_4>

<Candidate_5>
Workflow 5:
{workflow_5}
</Candidate_5>

<Candidate_6>
Workflow 6:
{workflow_6}
</Candidate_6>

<Candidate_7>
Workflow 7:
{workflow_7}
</Candidate_7>

<Candidate_8>
Workflow 8:
{workflow_8}
</Candidate_8>

<Candidate_9>
Workflow 9:
{workflow_9}
</Candidate_9>

<Candidate_10>
Workflow 10:
{workflow_10}
</Candidate_10>

### Note:
1. Please explain your choice using the <explanation></explanation> tags. For example: <explanation>This workflow is best suited to solve the user's query because it addresses all specified needs.</explanation>.
2. Provide the number of the chosen workflow and enclose it within <numbers></numbers> tags. For example: <numbers>3</numbers>.
3. Ensure that each tag appears only once in your response.

"""