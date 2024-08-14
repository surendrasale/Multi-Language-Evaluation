import pandas as pd
from difflib import SequenceMatcher

def similarity_percentage(s1, s2):
    """
    Calculate similarity percentage between two strings.
    """
    return SequenceMatcher(None, str(s1), str(s2)).ratio() * 100

def compare_answers(ground_truth, other_answers):
    """
    Compare the ground truth answer with other answers.
    """
    
    similarity_scores = []
    for answer in other_answers:
      
        similarity = similarity_percentage(ground_truth, answer)
        similarity_scores.append(similarity)
    return similarity_scores

def main(filename):
    # Read Excel file
    df = pd.read_excel(filename)

    # Extract ground truth answer and other answers
    ground_truth = df.iloc[0, 0]  # Assuming ground truth answer is in first row, first column
    other_answers = df.iloc[1:, 0].tolist()  # Assuming other answers are in subsequent rows of first column

    # Compare ground truth answer with other answers
    similarity_scores = compare_answers(ground_truth, other_answers)

    # Print comparison results
    print("Comparison Results:")
    for i, score in enumerate(similarity_scores):
        print(f"{score:.2f}")

# Example usage:
filename = 'compare.xlsx'
main(filename)
