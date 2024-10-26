# AI Assistant Bias Analysis Project

## Overview
This research project investigates bias in AI language models (specifically chat models) across multiple dimensions including nationality, religion, and immigrant status. The study employs a systematic approach using crime scenarios to analyze how AI models assign roles and make decisions about characters from diverse backgrounds.

## Research Methodology
The study employs the following methodology:

1. **Sample Selection**: 
   - 43 countries selected to ensure diverse representation across regions and religions
   - Coverage spans multiple geographical regions and religious backgrounds

2. **Scenario Generation**:
   - Each scenario involves four characters from different countries
   - Characters represent diverse regional and religious backgrounds
   - AI models are prompted to:
     - Assign gender and names to characters
     - Create a crime story featuring these characters
     - Identify the perpetrator of the crime

3. **Location Dynamics**:
   - Story setting is always one of the four characters' home countries
   - This creates a 3:1 ratio of immigrant to local characters in each scenario
   - Enables analysis of potential biases against immigrant characters

4. **Data Collection**:
   - Over 2,000 unique scenarios generated
   - Responses collected from multiple AI models:
     - OpenAI's ChatGPT
     - Anthropic's Claude
   - API integration used for consistent data collection

5. **Analysis Focus**:
   - Gender bias in character role assignment
   - Nationality-based discrimination
   - Immigrant status influence
   - Religious bias patterns

## Project Structure
```
project-root/
├── data/               # Dataset files and collected responses
├── scripts/            # Utility and analysis scripts
├── src/               # Source code for core functionality
├── general_config.json # Configuration parameters
└── main.py            # Main execution script
```

## Setup and Installation
1. Clone the repository:
```bash
git clone https://github.com/gsheikhi/AI_storyTelling_Bias.git
cd [repository-name]
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_key_here
     ANTHROPIC_API_KEY=your_anthropic_key_here
     ```

## Usage
1. Configure the parameters in `general_config.json`
2. Run the main script:
```bash
python main.py
```

## Data Privacy and Ethics
- All data collection adheres to API providers' terms of service
- No personally identifiable information is collected
- Research conducted with focus on ethical implications
- Results intended for academic and research purposes

## Contributing
We welcome contributions to this research project. Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
TODO

## Contact
TODO

## Acknowledgments
- TODO

---
**Note**: This is an ongoing research project. Findings and methodologies may be updated as the research progresses.