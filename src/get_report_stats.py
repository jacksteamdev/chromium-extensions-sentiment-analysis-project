def fnum(x: float):
    """Format a number with a fixed number of decimal places."""
    return f"{x:.7f}".rstrip("0").rstrip(".")


def get_report_stats(threads, markdown_report):
    thread_cost = 0
    thread_tokens = 0
    message_cost = 0
    message_tokens = 0
    for thread in threads:
        thread_cost += thread.get("total_cost", 0)
        thread_tokens += thread.get("total_tokens", 0)
        for message in thread.get("messages", []):
            message_cost += message.get("total_cost", 0)
            message_tokens += message.get("total_tokens", 0)

    report_cost = markdown_report.get("total_cost", 0)
    report_tokens = markdown_report.get("total_tokens", 0)
    total_cost = thread_cost + message_cost + report_cost
    total_tokens = thread_tokens + message_tokens + report_tokens

    print(f"Threads cost: ${fnum(thread_cost)}")
    print(f"Messages cost: ${fnum(message_cost)}")
    print(f"Report cost: ${fnum(report_cost)}")
    print(f"Total cost: ${fnum(total_cost)}")

    print(f"Thread tokens: {thread_tokens}")
    print(f"Message tokens: {message_tokens}")
    print(f"Report tokens: {report_tokens}")
    print(f"Total tokens: {total_tokens}")

    average_tokens_per_thread = thread_tokens / len(threads) if len(threads) else 0
    print(f"Average tokens per thread: {average_tokens_per_thread}")
    threads_per_million_tokens = (
        1e6 / average_tokens_per_thread if average_tokens_per_thread else 0
    )
    print(f"Threads per million tokens: {threads_per_million_tokens:.1f}")

    return {
        "total_cost": total_cost,
        "total_tokens": total_tokens,
        "report_cost": report_cost,
        "report_tokens": report_tokens,
        "thread_cost": thread_cost,
        "thread_tokens": thread_tokens,
        "message_cost": message_cost,
        "message_tokens": message_tokens,
        "average_tokens_per_thread": average_tokens_per_thread,
        "threads_per_million_tokens": threads_per_million_tokens,
    }
