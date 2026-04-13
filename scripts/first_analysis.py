from grievance_insights.analysis import summarize_counts


complaint_counts = [12, 18, 15, 21, 9]

total_complaints, average_complaints = summarize_counts(complaint_counts)

print(f"Total complaints in sample: {total_complaints}")
print(f"Average complaints per period: {average_complaints:.2f}")
