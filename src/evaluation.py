"""
Evaluation module for assessing research quality and agent performance.
Implements various metrics and scoring methods.
"""

import logging
from typing import Dict, Any, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchEvaluator:
    """Evaluates the quality of research outputs."""
    
    def __init__(self):
        pass
    
    def evaluate_comprehensiveness(self, data: Dict[str, List[Dict[str, Any]]]) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate comprehensiveness of data collection.
        Returns score (0-1) and details.
        """
        details = {}
        scores = []
        
        # Check coverage across different source types
        expected_sources = ['papers', 'repositories', 'news', 'discussions']
        present_sources = sum(1 for s in expected_sources if data.get(s) and len(data[s]) > 0)
        coverage_score = present_sources / len(expected_sources)
        details['source_coverage'] = {
            'present': present_sources,
            'total': len(expected_sources),
            'score': coverage_score
        }
        scores.append(coverage_score)
        
        # Check quantity of results
        total_items = sum(len(v) for v in data.values())
        quantity_score = min(total_items / 100, 1.0)  # Normalize to 0-1, capped at 100 items
        details['quantity'] = {
            'total_items': total_items,
            'score': quantity_score
        }
        scores.append(quantity_score)
        
        # Check quality of individual items (completeness of fields)
        quality_scores = []
        for category, items in data.items():
            if items:
                item = items[0]  # Sample first item
                required_fields = ['title', 'source']
                optional_fields = ['url', 'description', 'summary']
                
                required_present = sum(1 for f in required_fields if item.get(f))
                optional_present = sum(1 for f in optional_fields if item.get(f))
                
                item_score = (required_present / len(required_fields)) * 0.7 + \
                           (optional_present / len(optional_fields)) * 0.3
                quality_scores.append(item_score)
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        details['data_quality'] = {
            'score': avg_quality
        }
        scores.append(avg_quality)
        
        # Overall comprehensiveness score
        overall_score = sum(scores) / len(scores)
        
        return round(overall_score, 2), details
    
    def evaluate_relevance(self, query: str, data: Dict[str, List[Dict[str, Any]]]) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate relevance of collected data to the query.
        Returns score (0-1) and details.
        """
        details = {}
        query_terms = set(query.lower().split())
        
        relevance_scores = []
        
        for category, items in data.items():
            if not items:
                continue
            
            category_scores = []
            for item in items[:10]:  # Sample first 10 items
                # Check title relevance
                title = item.get('title', '').lower()
                description = item.get('description', item.get('summary', '')).lower()
                
                combined_text = f"{title} {description}"
                text_terms = set(combined_text.split())
                
                # Calculate term overlap
                overlap = len(query_terms.intersection(text_terms))
                relevance = overlap / len(query_terms) if query_terms else 0
                category_scores.append(min(relevance, 1.0))
            
            if category_scores:
                avg_category_score = sum(category_scores) / len(category_scores)
                relevance_scores.append(avg_category_score)
                details[category] = {
                    'avg_relevance': round(avg_category_score, 2),
                    'sample_size': len(category_scores)
                }
        
        overall_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        
        return round(overall_score, 2), details
    
    def evaluate_analysis_quality(self, analysis: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate quality of the analysis output.
        Returns score (0-1) and details.
        """
        details = {}
        scores = []
        
        # Check completeness of analysis sections
        required_sections = ['key_findings', 'summary', 'recommendations']
        present_sections = sum(1 for s in required_sections if analysis.get(s))
        completeness_score = present_sections / len(required_sections)
        details['completeness'] = {
            'present': present_sections,
            'total': len(required_sections),
            'score': completeness_score
        }
        scores.append(completeness_score)
        
        # Check depth of key findings
        key_findings = analysis.get('key_findings', [])
        avg_finding_length = 0
        if key_findings:
            avg_finding_length = sum(len(str(f)) for f in key_findings) / len(key_findings)
            depth_score = min(avg_finding_length / 100, 1.0)  # Expect ~100 chars per finding
        else:
            depth_score = 0
        
        details['depth'] = {
            'num_findings': len(key_findings),
            'avg_length': round(avg_finding_length, 1) if key_findings else 0,
            'score': depth_score
        }
        scores.append(depth_score)
        
        # Check summary quality
        summary = analysis.get('summary', '')
        if summary:
            # Good summary should be 100-500 chars
            summary_length = len(summary)
            if 100 <= summary_length <= 500:
                summary_score = 1.0
            elif summary_length < 100:
                summary_score = summary_length / 100
            else:
                summary_score = max(0.5, 1.0 - (summary_length - 500) / 1000)
        else:
            summary_score = 0
        
        details['summary_quality'] = {
            'length': len(summary),
            'score': summary_score
        }
        scores.append(summary_score)
        
        overall_score = sum(scores) / len(scores)
        
        return round(overall_score, 2), details
    
    def evaluate_output_formats(self, outputs: Dict[str, str]) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate quality of output formats.
        Returns score (0-1) and details.
        """
        details = {}
        scores = []
        
        # Check all required formats are present
        required_formats = ['markdown', 'json', 'html', 'bibtex', 'csv', 'mermaid']
        present_formats = sum(1 for f in required_formats if f in outputs and len(outputs[f]) > 0)
        format_score = present_formats / len(required_formats)
        details['format_completeness'] = {
            'present': present_formats,
            'total': len(required_formats),
            'score': format_score
        }
        scores.append(format_score)
        
        # Check quality of each format
        format_quality = {}
        
        # Markdown should have headers and content
        if 'markdown' in outputs:
            md = outputs['markdown']
            has_headers = '##' in md
            has_content = len(md) > 500
            md_score = (int(has_headers) + int(has_content)) / 2
            format_quality['markdown'] = md_score
        
        # JSON should be valid
        if 'json' in outputs:
            try:
                import json
                json.loads(outputs['json'])
                format_quality['json'] = 1.0
            except Exception:
                format_quality['json'] = 0.0
        
        # HTML should have basic structure
        if 'html' in outputs:
            html = outputs['html']
            has_doctype = '<!DOCTYPE' in html
            has_body = '<body>' in html
            html_score = (int(has_doctype) + int(has_body)) / 2
            format_quality['html'] = html_score
        
        if format_quality:
            quality_score = sum(format_quality.values()) / len(format_quality)
            scores.append(quality_score)
            details['format_quality'] = format_quality
        
        overall_score = sum(scores) / len(scores)
        
        return round(overall_score, 2), details
    
    def comprehensive_evaluation(self, 
                                 query: str,
                                 data: Dict[str, List[Dict[str, Any]]],
                                 analysis: Dict[str, Any],
                                 outputs: Dict[str, str]) -> Dict[str, Any]:
        """
        Perform comprehensive evaluation of the entire research process.
        Returns detailed evaluation report.
        """
        logger.info("Starting comprehensive evaluation...")
        
        # Evaluate each aspect
        comprehensiveness_score, comp_details = self.evaluate_comprehensiveness(data)
        relevance_score, rel_details = self.evaluate_relevance(query, data)
        analysis_score, analysis_details = self.evaluate_analysis_quality(analysis)
        output_score, output_details = self.evaluate_output_formats(outputs)
        
        # Calculate overall quality score (weighted average)
        weights = {
            'comprehensiveness': 0.25,
            'relevance': 0.30,
            'analysis': 0.25,
            'outputs': 0.20
        }
        
        overall_score = (
            comprehensiveness_score * weights['comprehensiveness'] +
            relevance_score * weights['relevance'] +
            analysis_score * weights['analysis'] +
            output_score * weights['outputs']
        )
        
        # Determine quality rating
        if overall_score >= 0.8:
            rating = "Excellent"
        elif overall_score >= 0.6:
            rating = "Good"
        elif overall_score >= 0.4:
            rating = "Fair"
        else:
            rating = "Needs Improvement"
        
        evaluation_report = {
            'overall_score': round(overall_score, 2),
            'rating': rating,
            'scores': {
                'comprehensiveness': comprehensiveness_score,
                'relevance': relevance_score,
                'analysis_quality': analysis_score,
                'output_quality': output_score
            },
            'details': {
                'comprehensiveness': comp_details,
                'relevance': rel_details,
                'analysis': analysis_details,
                'outputs': output_details
            },
            'recommendations': self._generate_recommendations(
                comprehensiveness_score,
                relevance_score,
                analysis_score,
                output_score
            )
        }
        
        logger.info(f"Evaluation complete: {rating} (score: {overall_score:.2f})")
        
        return evaluation_report
    
    def _generate_recommendations(self, comp_score: float, rel_score: float, 
                                  analysis_score: float, output_score: float) -> List[str]:
        """Generate recommendations for improvement."""
        recommendations = []
        
        if comp_score < 0.7:
            recommendations.append("Increase data collection from more diverse sources")
        
        if rel_score < 0.7:
            recommendations.append("Refine search terms to improve relevance of results")
        
        if analysis_score < 0.7:
            recommendations.append("Enhance analysis depth with more detailed findings")
        
        if output_score < 0.7:
            recommendations.append("Improve output format completeness and quality")
        
        if not recommendations:
            recommendations.append("Maintain current high quality standards")
        
        return recommendations
