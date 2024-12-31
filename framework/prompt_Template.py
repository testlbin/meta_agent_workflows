
workflow_Plan_Prompt = """
You are a workflow generation assistant, tasked with designing a workflow based on the user's input, converting the provided content into a structured workflow from the start node to the end node.

Instructions:

1.Follow the defined node types closely to determine which node to use.
2.Maintain the correct sequence of workflow steps and output the workflow as a JSON list.
3.The purpose of this workflow is to complete a specific set of tasks. The start node is used to input necessary information, and no LLM decision-making is required to determine API calls.
4.Node Explanation: Describe each node’s purpose and functionality within <explanation></explanation> tags, including any APIs used in HTTP requests. Use the exact API names as provided by the user, with no modifications.
5.Each HTTP request node must include accurate parameter details, including the following information:Parameter names and their purpose.Any hard-coded values required (e.g., a fixed API key). Dynamic values derived from user input or the output of other nodes.


<node information>
Node Definitions:
Start Node: The "Start" node is a predefined node essential for each workflow application (e.g., Chatflow/Workflow). It provides initial information necessary for the workflow's continued operation, such as input data from the application user.
LLM Node: Invokes the capability of large language models.
HTTP Request Node: HTTP Request Node: Allows sending requests via HTTP, suited for obtaining external data. This enables interaction with external services through customized HTTP requests.
End Node: Defines the final output of a workflow upon completion. Each workflow requires at least one end node to output the complete result after execution. The end node is the terminal point; no other nodes can follow it, and only upon reaching the end node does the application produce an output. It is also equal to the Finish node..
</node information>


Note:
1.Please explain the use of nodes in a specific workflow and wrap the explanations in <explanation></explanation> tags. For example: <explanation>The workflow contains the content of each node</explanation>.
2.Ensure that <explanation> tags contain parameter details for each HTTP request.
3.Please provide a summary of the workflow process in the form of a list, with each node as a string. Arrange the nodes in sequential order and wrap the list in <workflow></workflow> tags. For example: <workflow>['Start', 'HTTP request (API name)', 'End']</workflow>.


<example>
"<explanation>The workflow begins with the Start node to collect user input. Next, an HTTP Request node calls the 'UserVerification' API to verify user details. Another HTTP Request node calls the 'SubscriptionStatus' API to check subscription status. An If-Else node then branches based on subscription validity: if valid, an HTTP Request node calls the 'GetRecommendations' API to fetch personalized recommendations, ending with an End node that outputs these recommendations to the user.</explanation>",
"<workflow>['Start', 'HTTP request (UserVerification)', 'HTTP request (SubscriptionStatus)', 'If-Else', 'HTTP request (GetRecommendations)', 'End']</workflow>"
</example>

"""


json_regex = (
    r"""\{\n"""
    + r"""    "data": \{\n"""
    + r"""        "authorization": \{\n"""
    + r"""            "config": null,\n"""
    + r"""            "type": "no-auth"\n"""
    + r"""        \},\n"""
    + r"""        "body": \{\n"""
    + r"""            "data": ".*",\n"""
    + r"""            "type": "(none|raw text|json)"\n"""
    + r"""        \},\n"""
    + r"""        "desc": ".*",\n"""
    + r"""        "headers": ".*",\n"""
    + r"""        "method": "(get|post|put|delete|patch)",\n"""
    + r"""        "params": ".*",\n"""
    + r"""        "selected": (true|false),\n"""
    + r"""        "timeout": \{\n"""
    + r"""            "max_connect_timeout": \d+,\n"""
    + r"""            "max_read_timeout": \d+,\n"""
    + r"""            "max_write_timeout": \d+\n"""
    + r"""        \},\n"""
    + r"""        "title": "HTTP \\u8BF7\\u6C42",\n"""
    + r"""        "type": "http-request",\n"""
    + r"""        "url": "http[s]?:\/\/[\w\d\-\.]+\/[\w\d\-\.\/]*",\n"""
    + r"""        "variables": \[\]\n"""
    + r"""    \},\n"""
    + r"""\}"""
)

require= """
{
  "data": {
    "authorization": {
      "config": null,
      "type": "no-auth" // Required replacement: If the new API requires authentication, modify this section (e.g., for "bearer" authentication, changes are needed here).
    },
    "body": {
      "data": "{'test': '123456'}",
      "type": "json" // Required replacement: Modify according to the new API's data format and content.
    },
    "desc": "", // Optional: Used only to describe the function of the node, does not affect the request behavior.
    "headers": "", // Optional adjustment: Add custom request headers as needed by the new API, with each header on a new line within headers:.
    "method": "post", // Required replacement: Modify as needed based on the new API requirements; may need to change to "GET", "PUT", "DELETE", etc.
    "params": "", // Optional adjustment: Modify this section if the new API requires data to be passed through URL parameters, with each parameter on a new line within params:.
    "selected": false,
    "timeout": {
      "max_connect_timeout": 0,
      "max_read_timeout": 0,
      "max_write_timeout": 0 // Optional adjustment: Adjust timeout settings based on the response time of the new API.
    },
    "title": "HTTP Request",
    "type": "http-request", // Fixed
    "url": "", // Required replacement: Target URL of the new API.
    "variables": []
  }
}
"""