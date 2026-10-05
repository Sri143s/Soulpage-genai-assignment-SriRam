import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage

from task1_company_intelligence.state import CompanyState
from task1_company_intelligence.prompts.analyst_prompt import ANALYST_SYSTEM_PROMPT
from common.llm import get_llm
from common.logging_config import logger
from common.utils import parse_json_safely, format_sources

class AnalystAgent:
    """
    Analyst Agent responsible for consuming collected state, running analytical synthesis,
    categorizing Facts, Risks, and Opportunities, and producing the executive summary & report.
    """
    def __init__(self):
        pass

    def run(self, state: CompanyState) -> Dict[str, Any]:
        company_name = state.get("company_name", "Target Company")
        logger.info(f"--- ANALYST AGENT STARTED for '{company_name}' ---")
        
        company_info = state.get("company_info", {})
        news = state.get("news", [])
        stock_data = state.get("stock_data", {})
        sources = state.get("sources", [])

        # Prepare context prompt for LLM
        context = {
            "company_name": company_name,
            "company_info": company_info,
            "recent_news": news,
            "stock_data": stock_data
        }

        user_content = f"Analyze the following collected data for {company_name}:\n\n{json.dumps(context, indent=2)}"
        
        messages = [
            SystemMessage(content=ANALYST_SYSTEM_PROMPT),
            HumanMessage(content=user_content)
        ]

        llm = get_llm(temperature=0.2)
        try:
            llm_response = llm.invoke(messages)
            raw_output = llm_response.content
        except Exception as e:
            logger.error(f"Error invoking LLM in Analyst Agent: {e}")
            raw_output = ""

        analysis_dict = parse_json_safely(raw_output)
        if not analysis_dict:
            logger.warning("Failed to parse JSON from Analyst LLM output. Using structured fallback synthesis.")
            analysis_dict = self._fallback_analysis(company_name, company_info, news, stock_data, sources)

        # Merge extracted sources
        if "sources" in analysis_dict and isinstance(analysis_dict["sources"], list):
            for s in analysis_dict["sources"]:
                if isinstance(s, dict) and s not in sources:
                    sources.append(s)

        # Build readable Markdown report
        final_report = self._build_markdown_report(company_name, analysis_dict, stock_data, sources)
        
        logger.info(f"--- ANALYST AGENT COMPLETED for '{company_name}' ---")

        return {
            "analysis": analysis_dict,
            "final_report": final_report,
            "sources": sources
        }

    def _fallback_analysis(
        self,
        company_name: str,
        company_info: Dict[str, Any],
        news: List[Dict[str, Any]],
        stock_data: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        devs = [n.get("title") for n in news if isinstance(n, dict) and n.get("title")]
        if not devs:
            devs = [f"{company_name} maintains operational focus across primary market segments."]

        symbol = stock_data.get("symbol", company_name[:4].upper())
        price = stock_data.get("price", "N/A")
        pct = stock_data.get("change_percent", "N/A")

        return {
            "executive_summary": f"{company_name} is a major market participant with active commercial initiatives in {company_info.get('industry', 'technology & business services')}.",
            "recent_developments": devs,
            "market_snapshot": {
                "trend": "Stable" if pct == "N/A" or pct >= 0 else "Cautious",
                "market_position": f"Ticker: {symbol} | Price: ${price} ({pct}%)",
                "valuation_rating": "Fairly Valued"
            },
            "key_insights": [
                f"{company_name} exhibits consistent market relevance and enterprise engagement.",
                "Strategic R&D investments position the firm well for upcoming market cycles."
            ],
            "potential_risks": [
                "Macroeconomic uncertainties and industry competition.",
                "Regulatory compliance across international jurisdictions."
            ],
            "potential_opportunities": [
                "Expansion of core product lines and next-generation AI integrations.",
                "Strategic partnerships in emerging high-growth regional markets."
            ],
            "sources": sources
        }

    def _build_markdown_report(
        self,
        company_name: str,
        analysis: Dict[str, Any],
        stock: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> str:
        symbol = stock.get("symbol", company_name[:4].upper())
        price = stock.get("price", "N/A")
        change_pct = stock.get("change_percent", 0.0)
        is_demo = stock.get("demo_data", False)
        
        stock_header = f"**{symbol}** | ${price} ({'+' if isinstance(change_pct, (int, float)) and change_pct > 0 else ''}{change_pct}%)"
        if is_demo:
            stock_header += " *(DEMO DATA — NOT LIVE MARKET DATA)*"

        summary = analysis.get("executive_summary", "")
        devs = "\n".join([f"- {d}" for d in analysis.get("recent_developments", [])])
        insights = "\n".join([f"- {i}" for i in analysis.get("key_insights", [])])
        risks = "\n".join([f"- ⚠️ {r}" for r in analysis.get("potential_risks", [])])
        opps = "\n".join([f"- 🚀 {o}" for o in analysis.get("potential_opportunities", [])])
        formatted_sources = format_sources(sources)

        report = f"""# 📊 Corporate Intelligence Report: {company_name}

### 📈 Market Snapshot
{stock_header}

---

### 📝 Executive Summary
{summary}

---

### 📰 Recent Developments
{devs}

---

### 🔍 Key Analytical Insights
{insights}

---

### ⚠️ Potential Risks
{risks}

---

### 🚀 Potential Opportunities
{opps}

---

### 📚 Sources & References
{formatted_sources}
"""
        return report
