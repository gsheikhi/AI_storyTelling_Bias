"""
Lexical Bias Analysis for Crime Narratives
Analyzes linguistic patterns across 3 rounds and 2 models (ChatGPT and Claude)
"""

import pandas as pd
import numpy as np
import re
from collections import Counter
from scipy import stats
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

class LexicalBiasAnalyzer:
    """Analyzer for detecting lexical bias in narrative descriptions"""
    
    def __init__(self, base_dir='..'):
        """
        Initialize analyzer
        
        Parameters:
        - base_dir: Base directory relative to scripts folder (default: '..')
        """
        self.base_dir = Path(base_dir)
        self.data_processed = self.base_dir / 'data' / 'processed'
        self.data_results = self.base_dir / 'data' / 'results' / 'charactersANDcriminal_info'
        
        print("="*70)
        print("LEXICAL BIAS ANALYZER - INITIALIZATION")
        print("="*70)
        
        # Load all data
        self._load_data()
    
    def _load_data(self):
        """Load all narrative and extracted info files"""
        
        print("\n1. Loading narrative files...")
        print("-"*70)
        
        # ChatGPT narratives
        chatgpt_file = self.data_processed / 'chatgpt_responses.csv'
        print(f"Loading: {chatgpt_file}")
        self.chatgpt_narratives = pd.read_csv(chatgpt_file, sep=';', header=0, encoding='utf-8')
        print(f"  Columns: {self.chatgpt_narratives.columns.tolist()}")
        print(f"  Shape: {self.chatgpt_narratives.shape}")
        
        # Claude narratives
        claude_file = self.data_processed / 'claude_responses.csv'
        print(f"\nLoading: {claude_file}")
        self.claude_narratives = pd.read_csv(claude_file, sep=';', header=0, encoding='utf-8')
        print(f"  Columns: {self.claude_narratives.columns.tolist()}")
        print(f"  Shape: {self.claude_narratives.shape}")
        
        print("\n2. Loading extracted character info files...")
        print("-"*70)
        
        # Load extracted info for all rounds and models
        self.extracted_info = {}
        
        for model in ['chatgpt', 'claude']:
            self.extracted_info[model] = {}
            
            for round_num in [1, 2, 3]:
                # Note: Some filenames might be missing .csv extension dot
                filename = f'extracted_info_{model}_round{round_num}.csv'
                filepath = self.data_results / filename
                
                if not filepath.exists():
                    # Try without proper .csv extension (round2csv instead of round2.csv)
                    filename_alt = f'extracted_info_{model}_round{round_num}csv'
                    filepath = self.data_results / filename_alt
                
                if filepath.exists():
                    print(f"\nLoading: {filepath.name}")
                    df = pd.read_csv(filepath, sep=',', header=0, encoding='utf-8')
                    print(df.head(3))
                    print(f"  Columns: {df.columns.tolist()}")
                    print(f"  Shape: {df.shape}")
                    self.extracted_info[model][round_num] = df
                else:
                    print(f"\nWARNING: File not found: {filename}")
        
        print("\n" + "="*70)
        print("Data loading complete!")
        print("="*70)
    
    def _prepare_character_data(self, extracted_df, model, round_num):
        """
        Reshape extracted data from wide to long format
        Converts one row with 4 characters into 4 rows (one per character)
        
        Parameters:
        - extracted_df: DataFrame with columns like location, criminal, origin1-4, etc.
        - model: 'chatgpt' or 'claude'
        - round_num: 1, 2, or 3
        
        Returns:
        - DataFrame with one row per character
        """
        characters_list = []

        print(extracted_df.head(3))
        
        for idx, row in extracted_df.iterrows():
            location = row['location']
            criminal_char_num = row['criminal']  # Which character (1-4) is the criminal
            
            # Process each of the 4 characters
            for char_num in range(1, 5):
                # Extract character attributes
                origin = row.get(f'origin{char_num}')
                religion = row.get(f'religion{char_num}')
                name = row.get(f'name{char_num}')
                gender = row.get(f'gender{char_num}')
                
                # Skip if essential data is missing
                if pd.isna(name) or pd.isna(origin):
                    continue
                
                # Create character record
                char_data = {
                    'model': model,
                    'round': round_num,
                    'prompt_id': idx,
                    'location': str(location).strip() if pd.notna(location) else None,
                    'character_num': char_num,
                    'nationality': str(origin).strip() if pd.notna(origin) else None,
                    'religion': str(religion).strip() if pd.notna(religion) else 'Unknown',
                    'name': str(name).strip() if pd.notna(name) else None,
                    'gender': str(gender).strip() if pd.notna(gender) else 'Unknown',
                    'is_criminal': 1 if criminal_char_num == char_num else 0
                }
                
                # Determine migration status
                if pd.notna(origin) and pd.notna(location):
                    origin_clean = str(origin).strip().lower()
                    location_clean = str(location).strip().lower()
                    char_data['migration_status'] = 'native' if origin_clean == location_clean else 'foreign'
                else:
                    char_data['migration_status'] = 'unknown'
                
                characters_list.append(char_data)
        
        return pd.DataFrame(characters_list)
    
    def extract_character_description(self, narrative_text, char_name):
        """
        Extract sentences that mention a specific character
        
        Parameters:
        - narrative_text: Full story text
        - char_name: Character's name to search for
        
        Returns:
        - String containing all sentences mentioning this character
        """
        if pd.isna(narrative_text) or pd.isna(char_name):
            return ""
        
        narrative_text = str(narrative_text)
        char_name = str(char_name).strip()
        
        if not char_name or not narrative_text:
            return ""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', narrative_text)
        
        # Find sentences mentioning this character
        char_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Look for character name (word boundary to avoid partial matches)
            pattern = r'\b' + re.escape(char_name) + r'\b'
            if re.search(pattern, sentence, re.IGNORECASE):
                char_sentences.append(sentence)
        
        return ' '.join(char_sentences)
    
    def calculate_lexical_diversity(self, text):
        """
        Calculate lexical diversity metrics
        
        Returns dict with:
        - ttr: Type-Token Ratio
        - mattr: Moving Average Type-Token Ratio
        - hapax_ratio: Proportion of words used only once
        - total_words: Word count (after filtering)
        - unique_words: Number of unique words
        - avg_word_length: Average character length of words
        """
        if not text or pd.isna(text):
            return {
                'ttr': 0, 'mattr': 0, 'hapax_ratio': 0,
                'total_words': 0, 'unique_words': 0, 'avg_word_length': 0
            }
        
        # Tokenize: extract alphabetic words only
        words = re.findall(r'\b[a-zA-Z]+\b', str(text).lower())
        
        if not words:
            return {
                'ttr': 0, 'mattr': 0, 'hapax_ratio': 0,
                'total_words': 0, 'unique_words': 0, 'avg_word_length': 0
            }
        
        # Remove common stop words to focus on content
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'were', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her'
        }
        
        content_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        if not content_words:
            content_words = words  # Fallback
        
        # Type-Token Ratio (TTR)
        unique_words = set(content_words)
        ttr = len(unique_words) / len(content_words) if content_words else 0
        
        # Moving Average TTR (MATTR) - more stable across text lengths
        window_size = min(50, len(content_words))
        if len(content_words) < window_size:
            mattr = ttr
        else:
            ttrs = []
            for i in range(len(content_words) - window_size + 1):
                window = content_words[i:i + window_size]
                window_ttr = len(set(window)) / len(window)
                ttrs.append(window_ttr)
            mattr = np.mean(ttrs)
        
        # Hapax legomena ratio (words appearing only once)
        word_freq = Counter(content_words)
        hapax_count = sum(1 for count in word_freq.values() if count == 1)
        hapax_ratio = hapax_count / len(unique_words) if unique_words else 0
        
        # Average word length
        avg_word_length = np.mean([len(w) for w in content_words]) if content_words else 0
        
        return {
            'ttr': round(ttr, 4),
            'mattr': round(mattr, 4),
            'hapax_ratio': round(hapax_ratio, 4),
            'total_words': len(content_words),
            'unique_words': len(unique_words),
            'avg_word_length': round(avg_word_length, 2)
        }
    
    def calculate_word_frequency_profile(self, text):
        """
        Analyze word frequency distribution
        High-frequency words = common, "safe" words
        Rare words = more diverse, specific vocabulary
        
        Returns dict with:
        - high_freq_ratio: Proportion of high-frequency words
        - rare_word_ratio: Proportion of rare/uncommon words
        """
        if not text or pd.isna(text):
            return {'high_freq_ratio': 0, 'rare_word_ratio': 0}
        
        words = re.findall(r'\b[a-zA-Z]+\b', str(text).lower())
        words = [w for w in words if len(w) > 2]
        
        if not words:
            return {'high_freq_ratio': 0, 'rare_word_ratio': 0}
        
        # Top ~100 most common English words
        common_words = {
            'the', 'be', 'to', 'of', 'and', 'in', 'that', 'have', 'it', 'for',
            'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but',
            'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an',
            'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'was',
            'were', 'been', 'has', 'had', 'who', 'when', 'where', 'why', 'how',
            'about', 'after', 'before', 'because', 'between', 'through', 'during',
            'good', 'new', 'first', 'last', 'long', 'great', 'little', 'own', 'other',
            'old', 'right', 'big', 'high', 'different', 'small', 'large', 'next',
            'man', 'woman', 'people', 'person', 'child', 'family', 'friend', 'life',
            'time', 'year', 'day', 'way', 'world', 'work', 'place', 'home', 'hand',
            'know', 'take', 'come', 'think', 'see', 'get', 'make', 'go', 'look',
            'want', 'give', 'use', 'find', 'tell', 'ask', 'work', 'seem', 'feel'
        }
        
        # Calculate ratios
        high_freq_count = sum(1 for w in words if w in common_words)
        high_freq_ratio = high_freq_count / len(words)
        rare_word_ratio = 1 - high_freq_ratio
        
        return {
            'high_freq_ratio': round(high_freq_ratio, 4),
            'rare_word_ratio': round(rare_word_ratio, 4)
        }
    
    def analyze_all_narratives(self):
        """
        Main analysis function
        Processes all narratives across both models and all rounds
        
        Returns:
        - DataFrame with lexical metrics for each character in each narrative
        """
        print("\n" + "="*70)
        print("ANALYZING NARRATIVES")
        print("="*70)
        
        all_results = []
        
        # Process each model
        for model_name in ['chatgpt', 'claude']:
            print(f"\n{'='*70}")
            print(f"Processing {model_name.upper()}")
            print(f"{'='*70}")
            
            # Get narratives for this model
            if model_name == 'chatgpt':
                narratives_df = self.chatgpt_narratives
            else:
                narratives_df = self.claude_narratives
            
            # Process each round
            for round_num in [1, 2, 3]:
                print(f"\n  Round {round_num}:")
                print(f"  {'-'*66}")
                
                # Get extracted info for this model and round
                if round_num not in self.extracted_info[model_name]:
                    print(f"  WARNING: No extracted info for {model_name} round {round_num}")
                    continue
                
                extracted_df = self.extracted_info[model_name][round_num]
                
                # Prepare character data (wide to long format)
                characters_df = self._prepare_character_data(extracted_df, model_name, round_num)
                print(f"  Characters to analyze: {len(characters_df)}")
                
                # Column name for this round's narratives
                narrative_col = f'round{round_num}'
                
                if narrative_col not in narratives_df.columns:
                    print(f"  ERROR: Column '{narrative_col}' not found in narratives")
                    continue
                
                # Process each character
                processed = 0
                for idx, char in characters_df.iterrows():
                    prompt_id = char['prompt_id']
                    
                    # Get narrative for this prompt
                    if prompt_id >= len(narratives_df):
                        continue
                    
                    narrative_text = narratives_df.iloc[prompt_id][narrative_col]
                    
                    if pd.isna(narrative_text):
                        continue
                    
                    # Extract character description
                    char_description = self.extract_character_description(
                        narrative_text,
                        char['name']
                    )
                    
                    # Calculate metrics
                    diversity = self.calculate_lexical_diversity(char_description)
                    frequency = self.calculate_word_frequency_profile(char_description)
                    
                    # Combine all data
                    result = {
                        'model': model_name,
                        'round': round_num,
                        'prompt_id': prompt_id,
                        'character_num': char['character_num'],
                        'nationality': char['nationality'],
                        'religion': char['religion'],
                        'gender': char['gender'],
                        'migration_status': char['migration_status'],
                        'is_criminal': char['is_criminal'],
                        'description_length': len(char_description),
                        **diversity,
                        **frequency
                    }
                    
                    all_results.append(result)
                    processed += 1
                
                print(f"  Processed: {processed} characters")
        
        # Create results DataFrame
        self.lexical_results = pd.DataFrame(all_results)
        
        print("\n" + "="*70)
        print("ANALYSIS SUMMARY")
        print("="*70)
        print(f"Total character descriptions analyzed: {len(self.lexical_results)}")
        
        # Show breakdown
        valid = self.lexical_results[self.lexical_results['total_words'] > 0]
        print(f"Valid descriptions (with text): {len(valid)}")
        print(f"\nBy model:")
        print(self.lexical_results.groupby('model').size())
        print(f"\nBy round:")
        print(self.lexical_results.groupby('round').size())
        
        if len(valid) > 0:
            print(f"\nAverage words per description: {valid['total_words'].mean():.2f}")
            print(f"Average TTR: {valid['ttr'].mean():.4f}")
        
        return self.lexical_results
    
    def compare_groups(self, dimension='nationality', metric='ttr'):
        """
        Statistical comparison across demographic groups
        
        Parameters:
        - dimension: 'nationality', 'religion', 'gender', 'migration_status'
        - metric: 'ttr', 'unique_words', 'high_freq_ratio', etc.
        """
        print(f"\n{'='*70}")
        print(f"COMPARING {metric.upper()} BY {dimension.upper()}")
        print(f"{'='*70}\n")
        
        valid_data = self.lexical_results[self.lexical_results['total_words'] > 0]
        
        if len(valid_data) == 0:
            print("No valid data to analyze")
            return None
        
        # Summary statistics
        summary = valid_data.groupby(dimension).agg({
            'ttr': ['mean', 'std', 'count'],
            'unique_words': ['mean', 'std'],
            'total_words': ['mean', 'std'],
            'high_freq_ratio': ['mean', 'std']
        }).round(4)
        
        print("Summary Statistics:")
        print(summary)
        print()
        
        # ANOVA test
        groups = valid_data[dimension].dropna().unique()
        metric_by_group = [
            valid_data[valid_data[dimension] == g][metric].dropna().values
            for g in groups
            if len(valid_data[valid_data[dimension] == g]) > 0
        ]
        metric_by_group = [g for g in metric_by_group if len(g) > 0]
        
        if len(metric_by_group) > 1:
            try:
                f_stat, p_value = stats.f_oneway(*metric_by_group)
                print(f"ANOVA Test:")
                print(f"  F-statistic: {f_stat:.4f}")
                print(f"  p-value: {p_value:.4f}")
                
                if p_value < 0.05:
                    print("  *** SIGNIFICANT DIFFERENCE DETECTED ***")
                else:
                    print("  No significant difference")
            except Exception as e:
                print(f"  Could not perform ANOVA: {e}")
        
        return summary
    
    def compare_models(self, dimension='nationality', metric='ttr'):
        """Compare lexical patterns between ChatGPT and Claude"""
        print(f"\n{'='*70}")
        print(f"MODEL COMPARISON: {metric.upper()} BY {dimension.upper()}")
        print(f"{'='*70}\n")
        
        valid_data = self.lexical_results[self.lexical_results['total_words'] > 0]
        
        for model in ['chatgpt', 'claude']:
            model_data = valid_data[valid_data['model'] == model]
            print(f"\n{model.upper()}:")
            print("-" * 70)
            
            summary = model_data.groupby(dimension)[metric].agg(['mean', 'std', 'count']).round(4)
            print(summary)
    
    def generate_report(self, output_file='lexical_bias_report.txt'):
        """Generate comprehensive text report"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("LEXICAL BIAS ANALYSIS REPORT\n")
            f.write("Crime Narrative Character Descriptions\n")
            f.write("="*80 + "\n\n")
            
            valid_data = self.lexical_results[self.lexical_results['total_words'] > 0]
            
            # Overall statistics
            f.write("OVERALL STATISTICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Total descriptions: {len(self.lexical_results)}\n")
            f.write(f"Valid descriptions: {len(valid_data)}\n")
            f.write(f"Avg words/description: {valid_data['total_words'].mean():.2f}\n")
            f.write(f"Avg TTR: {valid_data['ttr'].mean():.4f}\n\n")
            
            # By model
            f.write("BY MODEL\n")
            f.write("-"*80 + "\n")
            for model in ['chatgpt', 'claude']:
                model_data = valid_data[valid_data['model'] == model]
                f.write(f"\n{model.upper()}:\n")
                f.write(f"  Count: {len(model_data)}\n")
                f.write(f"  Avg TTR: {model_data['ttr'].mean():.4f}\n")
                f.write(f"  Avg unique words: {model_data['unique_words'].mean():.2f}\n")
            
            # By dimension
            for dimension in ['nationality', 'religion', 'gender', 'migration_status']:
                f.write(f"\n{'='*80}\n")
                f.write(f"BY {dimension.upper()}\n")
                f.write("="*80 + "\n\n")
                
                summary = valid_data.groupby(dimension).agg({
                    'ttr': ['mean', 'std', 'count'],
                    'unique_words': ['mean'],
                    'high_freq_ratio': ['mean']
                }).round(4)
                
                f.write(str(summary) + "\n\n")
                
                # ANOVA
                groups = valid_data[dimension].dropna().unique()
                ttr_by_group = [
                    valid_data[valid_data[dimension] == g]['ttr'].dropna().values
                    for g in groups
                ]
                ttr_by_group = [g for g in ttr_by_group if len(g) > 0]
                
                if len(ttr_by_group) > 1:
                    try:
                        f_stat, p_value = stats.f_oneway(*ttr_by_group)
                        f.write(f"ANOVA: F={f_stat:.4f}, p={p_value:.4f}\n")
                        if p_value < 0.05:
                            f.write("*** SIGNIFICANT ***\n")
                    except:
                        pass
        
        print(f"\nReport saved to: {output_file}")
    
    def save_results(self, output_file='lexical_analysis_results.csv'):
        """Save detailed results to CSV"""
        self.lexical_results.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Results saved to: {output_file}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("LEXICAL BIAS ANALYSIS")
    print("Crime Narratives - ChatGPT vs Claude - 3 Rounds")
    print("="*70 + "\n")
    
    # Initialize analyzer (from scripts folder, go up one level to reach data)
    analyzer = LexicalBiasAnalyzer(base_dir='..')
    
    # Run full analysis
    results = analyzer.analyze_all_narratives()
    
    # Comparative analyses
    print("\n" + "="*70)
    print("DEMOGRAPHIC COMPARISONS")
    print("="*70)
    
    for dimension in ['nationality', 'religion', 'gender', 'migration_status']:
        analyzer.compare_groups(dimension=dimension, metric='ttr')
    
    # Model comparison
    print("\n" + "="*70)
    print("MODEL COMPARISONS")
    print("="*70)
    
    analyzer.compare_models(dimension='nationality', metric='ttr')
    
    # Generate outputs
    print("\n" + "="*70)
    print("GENERATING OUTPUTS")
    print("="*70)
    
    analyzer.generate_report('data/results/lexical_analysis/lexical_bias_report.txt')
    analyzer.save_results('data/results/lexical_analysis/lexical_analysis_results.csv')
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE!")
    print("="*70)
    print("\nOutput files:")
    print("  - lexical_bias_report.txt")
    print("  - lexical_analysis_results.csv")
    print()