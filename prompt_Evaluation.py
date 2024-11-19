
"""
Consistency
"""

prompt_Consistency = """
Please assess the consistency of the following data. Compare the original tool trajectory with the converted workflow JSON data and determine if the converted data maintains the exact flow and structure of the original.

Ensure that each request aligns in sequence and content, and note any omissions, discrepancies, or inconsistencies.
Provide a score from 1 to 10 based on the following criteria:

10 points: Completely consistent with no mismatches or omissions.
7-9 points: Most nodes are consistent, with minor omissions or partial mismatches.
4-6 points: Some nodes are inconsistent, with notable omissions or errors.
1-3 points: Most nodes do not match; the structure is largely misaligned with the original.

Note:
1. Please provide an explanation within <explanation></explanation> tags.
2. Please provide the consistency score in <score></score> tags. For example: <score>10</score>.
3. Please ensure that each tag appears only once.

Please provide a final score and briefly explain your reasoning.
"""

"""
Accuracy
"""

prompt_Accuracy = """
Please evaluate the accuracy of the following data, assessing whether the converted JSON data accurately includes all critical information for each request (e.g., URL, method, parameters).

Check if each field is correctly converted and whether any critical information is missing or misinterpreted.
Provide a score from 1 to 10 based on the following criteria:

10 points: All fields are correctly converted, with no critical errors.
7-9 points: Minor fields are missing or contain small errors, but critical fields are accurate.
4-6 points: Multiple fields contain errors or are missing, and some critical information is misinterpreted.
1-3 points: Critical information is severely lacking; the conversion accuracy is extremely low.
Note:
1. Please provide an explanation within <explanation></explanation> tags.
2. Please provide the consistency score in <score></score> tags. For example: <score>10</score>.
3. Please ensure that each tag appears only once.

Please provide a final score and briefly explain your reasoning.

"""


"""
Order Accuracy
"""

prompt_Order_Accuracy = """
Please assess the order accuracy of the following data, checking whether the converted JSON data preserves the exact sequence of the original request trajectory.

Provide a score from 1 to 10 based on the following criteria:

10 points: All requests are in the exact order.
7-9 points: A few steps are out of order, but the overall logic is unaffected.
4-6 points: Multiple steps are out of order, causing partial deviation in workflow logic.
1-3 points: Most steps are out of order; the flow logic is significantly disrupted.

Note:
1. Please provide an explanation within <explanation></explanation> tags.
2. Please provide the consistency score in <score></score> tags. For example: <score>10</score>.
3. Please ensure that each tag appears only once.

Please provide a final score and briefly explain your reasoning.

"""

"""
Readability
"""

prompt_Readability = """
Please evaluate the readability of the following data, assessing whether the converted JSON data is clear and well-structured, making it suitable for subsequent analysis and understanding. Pay attention to the clarity of field names and the organization of the structure.

Provide a score from 1 to 10 based on the following criteria:

10 points: Field names are clear, and the structure is well-organized, making it highly readable.
7-9 points: Minor issues with fields or structure affect readability slightly, but it remains overall clear.
4-6 points: Several fields or structure levels are poorly named or organized, making it challenging to understand.
1-3 points: The structure is confusing, with unclear naming, making the JSON difficult to read.

Note:
1. Please provide an explanation within <explanation></explanation> tags.
2. Please provide the consistency score in <score></score> tags. For example: <score>10</score>.
3. Please ensure that each tag appears only once.

Please provide a final score and briefly explain your reasoning.

"""

"""
Reusability
"""

prompt_Reusability = """
Please assess the reusability of the following data, evaluating whether the converted JSON format is designed in a way that supports reusability for different request trajectories. Consider whether field designs and structures are adaptable for reuse in other scenarios.

Provide a score from 1 to 10 based on the following criteria:

10 points: The JSON format is well-designed to support reuse across different request trajectories.
7-9 points: Minor issues with fields or structure impact reusability slightly, but overall compatibility is good.
4-6 points: Multiple fields limit reusability, resulting in limited adaptability.
1-3 points: The structure is not well-suited for reuse or extension.

Note:
1. Please provide an explanation within <explanation></explanation> tags.
2. Please provide the consistency score in <score></score> tags. For example: <score>10</score>.
3. Please ensure that each tag appears only once.

Please provide a final score and briefly explain your reasoning.

"""


input_Template = """
### Origin Trajectory:
<trajectory>
{trajectory}
</trajectory>


### Json Workflow:
<workflow>
{workflow}
</workflow>

"""
