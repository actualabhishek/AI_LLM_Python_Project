#%%

#%%
import json

from inventory import get_device_by_name
from network_tools import execute_command
from ai import get_ai_response


# =========================
# TOOL DEFINITIONS
# =========================

tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Run Cisco IOS show commands safely",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Name of network device"
                    },
                    "command": {
                        "type": "string",
                        "description": "Cisco IOS show command"
                    }
                },
                "required": ["device_name", "command"]
            }
        }
    }
]


# =========================
# SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """
You are a senior Cisco TAC automation engineer operating as an autonomous troubleshooting agent.

You must independently troubleshoot Cisco devices using tools.

RULES:
- Use tools proactively
- Execute safe commands autonomously
- Never ask user to run commands manually
- Never use config mode
- Never use debug/clear/reload commands
- Stop after enough evidence is collected
- Avoid repeating same commands endlessly

ALLOWED:
- show commands
- limited ping
- limited traceroute

STOP CONDITIONS:
- Root cause identified
- Enough evidence collected
- No further useful commands available

Always provide:
1. Investigation Performed
2. Findings
3. Root Cause
4. Recommended Fix
5. Risk Assessment
"""


# =========================
# MAIN CHAT LOOP
# =========================

while True:

    user_input = input("\nIssue: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Exiting...")
        break

    # Fresh conversation per issue
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    # Prevent infinite loops
    max_iterations = 10
    iteration = 0

    # Track executed commands
    executed_commands = set()

    try:

        # =========================
        # AGENT LOOP
        # =========================

        while iteration < max_iterations:

            iteration += 1

            print(f"\n========== ITERATION {iteration} ==========")

            # -------------------------
            # LLM CALL
            # -------------------------

            response = get_ai_response(
                messages=messages,
                tools=tools
            )

            response_message = response.choices[0].message

            print("\n========== RAW AI RESPONSE ==========")
            print(response_message)
            print("=====================================\n")

            # Save COMPLETE assistant message
            messages.append(response_message)

            # -------------------------
            # FINAL RESPONSE
            # -------------------------

            if (
                not response_message.tool_calls
                and response_message.content
            ):

                print("\n========== AI ANALYSIS ==========")
                print(response_message.content)
                print("=================================\n")

                break

            # -------------------------
            # TOOL EXECUTION
            # -------------------------

            for tool_call in response_message.tool_calls:

                try:

                    function_name = tool_call.function.name

                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                    device_name = arguments["device_name"]
                    command = arguments["command"]

                    print("\nExecuting Tool...")
                    print(f"Function : {function_name}")
                    print(f"Device   : {device_name}")
                    print(f"Command  : {command}")

                    # -------------------------
                    # DUPLICATE COMMAND CHECK
                    # -------------------------

                    command_key = (
                        device_name,
                        command
                    )

                    if command_key in executed_commands:

                        tool_result = (
                            "Command already executed previously."
                        )

                    else:

                        executed_commands.add(command_key)

                        # -------------------------
                        # GET DEVICE
                        # -------------------------

                        device = get_device_by_name(
                            device_name
                        )

                        if not device:

                            tool_result = (
                                f"Device '{device_name}' not found."
                            )

                        else:

                            # -------------------------
                            # EXECUTE COMMAND
                            # -------------------------

                            tool_result = execute_command(
                                device,
                                command
                            )

                    # -------------------------
                    # PRINT OUTPUT
                    # -------------------------

                    print("\n========== DEVICE OUTPUT ==========")
                    print(tool_result)
                    print("===================================\n")

                    # -------------------------
                    # APPEND TOOL RESULT
                    # -------------------------

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result)
                    })

                except Exception as tool_error:

                    error_message = (
                        f"Tool execution failed: {str(tool_error)}"
                    )

                    print("\nTOOL ERROR:")
                    print(error_message)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": error_message
                    })

        # =========================
        # MAX ITERATION EXIT
        # =========================

        else:

            print("\n========== AGENT STOPPED ==========")
            print("Maximum iterations reached.")
            print("===================================\n")

    except Exception as e:

        print("\n========== ERROR ==========")
        print(str(e))
        print("===========================\n")
#%%

#%%
