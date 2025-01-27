from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from typing import Dict, Optional, List, Tuple
import json
import logging
from datetime import datetime

load_dotenv()

class PublicationAnalyzer:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OpenAI API key in environment variables")
            
        self.client = AsyncOpenAI(api_key=api_key)
        self.logger = logging.getLogger(__name__)
        
        # Define detailed evaluation criteria with weights and subcriteria
        self.evaluation_criteria = {
            'innovation': {
                'weight': 0.25,
                'subcriteria': {
                    'novelty': 'Uniqueness of the solution',
                    'technological_advancement': 'Level of technological innovation',
                    'patent_potential': 'Potential for IP protection'
                }
            },
            'market_potential': {
                'weight': 0.25,
                'subcriteria': {
                    'market_size': 'Total addressable market size',
                    'growth_potential': 'Market growth trajectory',
                    'customer_need': 'Strength of market demand'
                }
            },
            'technical_feasibility': {
                'weight': 0.20,
                'subcriteria': {
                    'implementation_complexity': 'Ease of implementation',
                    'scalability': 'Ability to scale the solution',
                    'resource_requirements': 'Required resources and infrastructure'
                }
            },
            'competitive_advantage': {
                'weight': 0.15,
                'subcriteria': {
                    'differentiation': 'Uniqueness compared to competitors',
                    'barriers_to_entry': 'Defensibility of the solution',
                    'cost_advantage': 'Cost-effectiveness of the solution'
                }
            },
            'commercialization_readiness': {
                'weight': 0.15,
                'subcriteria': {
                    'development_stage': 'Current stage of development',
                    'time_to_market': 'Expected time to commercialization',
                    'regulatory_requirements': 'Regulatory compliance needs'
                }
            }
        }

    async def analyze_publication(self, publication_data: Dict) -> Optional[Dict]:
        """Analyze a publication for its commercial and startup potential."""
        try:
            sanitized_data = self._sanitize_publication_data(publication_data)
            initial_analysis = await self._get_gpt_analysis(sanitized_data)
            
            if not initial_analysis:
                return None

            # Get detailed scoring with explanations
            detailed_scores = await self._get_detailed_scoring(sanitized_data, initial_analysis)
            
            # Calculate final weighted score
            final_score = self._calculate_final_score(detailed_scores)
            
            result = {
                'publication_id': publication_data.get('id'),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'startup_potential_score': final_score,
                'detailed_analysis': {
                    'summary': initial_analysis.get('summary', ''),
                    'scores_and_reasoning': detailed_scores,
                    'market_analysis': initial_analysis.get('market_analysis', ''),
                    'technical_assessment': initial_analysis.get('technical_assessment', ''),
                    'commercialization_strategy': initial_analysis.get('recommended_path', '')
                },
                'key_metrics': {
                    'estimated_time_to_market': initial_analysis.get('time_to_market_months', 0),
                    'required_investment_level': initial_analysis.get('required_investment', 'medium'),
                    'risk_level': initial_analysis.get('risk_level', 'medium')
                },
                'recommendations': {
                    'next_steps': initial_analysis.get('recommended_next_steps', []),
                    'potential_partners': initial_analysis.get('potential_partners', []),
                    'funding_sources': initial_analysis.get('funding_sources', [])
                }
            }
            
            self.logger.info(f"Successfully analyzed publication with score {final_score}: {sanitized_data['title']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in publication analysis: {e}")
            return None

    async def _get_detailed_scoring(self, publication_data: Dict, initial_analysis: Dict) -> Dict:
        """Get detailed scores with explanations for each criterion."""
        try:
            prompt = self._create_detailed_scoring_prompt(publication_data, initial_analysis)
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert in evaluating research commercialization potential.
                        For each criterion, provide:
                        1. A score from 0-100
                        2. A detailed explanation of the score
                        3. Specific evidence from the publication
                        4. Potential risks and opportunities
                        
                        Format your response as a JSON object with each main criterion containing:
                        - score: numerical score
                        - explanation: detailed reasoning
                        - evidence: list of supporting evidence
                        - risks: list of potential risks
                        - opportunities: list of potential opportunities"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={ "type": "json_object" },
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Error in detailed scoring: {e}")
            return {}

    def _create_detailed_scoring_prompt(self, publication_data: Dict, initial_analysis: Dict) -> str:
        """Create a prompt for detailed scoring analysis."""
        criteria_descriptions = "\n".join(
            f"{criterion}:\n" + "\n".join(f"- {sub}: {desc}" 
            for sub, desc in details['subcriteria'].items())
            for criterion, details in self.evaluation_criteria.items()
        )
        
        return f"""
        Provide a detailed scoring analysis for this publication:
        
        Title: {publication_data['title']}
        Abstract: {publication_data['abstract']}
        
        Initial Analysis Summary:
        {initial_analysis.get('summary', '')}
        
        Please evaluate each criterion:
        
        {criteria_descriptions}
        
        For each criterion:
        1. Assign a score (0-100)
        2. Explain your reasoning
        3. Cite specific evidence from the publication
        4. Identify risks and opportunities
        
        Focus on concrete, practical aspects of commercialization potential.
        """

    def _calculate_final_score(self, detailed_scores: Dict) -> float:
        """Calculate the final weighted score with detailed criteria."""
        try:
            weighted_sum = 0
            for criterion, details in self.evaluation_criteria.items():
                if criterion in detailed_scores:
                    criterion_score = detailed_scores[criterion].get('score', 0)
                    weighted_sum += criterion_score * details['weight']
            
            # Convert to 1-10 scale and round to one decimal
            return round(weighted_sum / 100 * 10, 1)
        except Exception as e:
            self.logger.error(f"Error calculating final score: {e}")
            return 0.0

    async def _get_gpt_analysis(self, publication_data: Dict) -> Optional[Dict]:
        """Get the GPT-4 analysis of the publication."""
        try:
            prompt = self._create_analysis_prompt(publication_data)
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert in analyzing academic research for commercial viability and startup potential.
                        Analyze the given publication data and provide a detailed assessment of its commercial potential.
                        Focus on concrete applications, market opportunities, and implementation feasibility.
                        Be critical and realistic in your assessment.
                        
                        Return your analysis in JSON format with numerical scores (0-100) for:
                        - innovation_score: novelty and uniqueness of the solution
                        - market_potential: size and accessibility of target market
                        - technical_feasibility: technical complexity and implementation challenges
                        - implementation_readiness: current stage of development
                        - competitive_advantage: strength compared to existing solutions
                        
                        Also include:
                        - summary: Brief overview of commercial potential
                        - innovation_analysis: Detailed assessment of the innovation
                        - market_analysis: Market opportunity assessment
                        - technical_assessment: Technical feasibility evaluation
                        - recommended_path: Suggested commercialization approach
                        - key_challenges: List of main obstacles
                        - target_industries: List of relevant industries
                        - time_to_market_months: Estimated months to market
                        - required_resources: List of needed resources"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={ "type": "json_object" },
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Error getting GPT analysis: {e}")
            return None

    def _create_analysis_prompt(self, publication_data: Dict) -> str:
        """Create a detailed prompt for GPT analysis."""
        return f"""
        Analyze this research publication for its commercial and startup potential:
        
        Title: {publication_data['title']}
        
        Abstract:
        {publication_data['abstract']}
        
        Department: {publication_data['department']}
        Publication Type: {publication_data['publication_type']}
        
        Consider:
        1. What unique problem does this research solve?
        2. Is there a clear market need for this solution?
        3. How technically feasible is implementation?
        4. What resources would be needed for commercialization?
        5. What are the main technical and market risks?
        6. How does this compare to existing solutions?
        7. What is the potential market size and accessibility?
        8. How long would it take to bring this to market?
        
        Provide a comprehensive analysis focusing on practical commercial applications.
        """

    def _sanitize_publication_data(self, publication_data: Dict) -> Dict:
        """Remove sensitive information and prepare data for analysis."""
        return {
            'id': publication_data.get('id', ''),
            'title': publication_data.get('title', ''),
            'abstract': publication_data.get('abstract', ''),
            'department': publication_data.get('department', ''),
            'publication_type': publication_data.get('publication_type', ''),
            'publication_date': publication_data.get('publication_date', '')
        } 