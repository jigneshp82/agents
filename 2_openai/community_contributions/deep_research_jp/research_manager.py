from csv import writer
from email_agent import email_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from search_agent import search_agent
from report_agent import report_agent, ReportData
from agents import Runner, trace, gen_trace_id
from clarifiing_questions import clarifiing_agent, Questions
import asyncio

class ResearchManager:
    async def plan_searches(self,query:str) ->WebSearchPlan:
        #Plan the searches to perform the query
        print("planning Searches")
        result = await Runner.run(planner_agent,f"Query: {query}")
        print (f"Total Searches found : {len(result.final_output.searches)}")
        return result.final_output_as(WebSearchPlan)

    async def execute_search(self, search_plan:WebSearchPlan)-> list[str]:
        #Plan the searches to perform the query
        print("executeing Searches")
        completed = 0 
        results = []
        tasks = [asyncio.create_task(self.search(_)) for _ in search_plan.searches]
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            completed +=1
            print (f"Searching ... {completed} / {len(tasks)}")
        print ("searching done")
        return results


    async def search(self,search_item:WebSearchItem) -> str | None:
        #Plan the searches to perform the query
        input = f"Search term : {search_item.query} \nReason: {search_item.reason}"
        try:
            res = await Runner.run(search_agent,input)
            return str(res.final_output)
        except Exception:
            print ("Error in Search agent")
            return None


    async def writeReport(self,query:str,search_res:list[str])-> ReportData:
        #Write Report for the query
        print ("writing report")
        input = f"Original query : {query}\nsearch result:{search_res}"
        res = await Runner.run(report_agent,input)
        print("Finished Writeing Report")
        return res.final_output_as(ReportData)


    async def emailReport(self, report:ReportData)-> None:
        print ("Sending Email")
        res = await Runner.run(email_agent,report.markdwonReport)
        print("email sent")
        return (res)

    async def askclarifingQuestion(self, query) -> Questions:
        print ("asking more questions")
        res = await Runner.run(clarifiing_agent, query)
        return res.final_output_as(Questions)

    async def run(self, query:str):
        traceID = gen_trace_id()
        with trace("Deep Research trace", trace_id = traceID):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={traceID}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={traceID}"
            print("Starting research...")
            search_plan = await self.plan_searches(query)
            yield f'Search Planning done'
            searches = await self.execute_search(search_plan)
            yield "Search Complete Now generating report"
            report = await self.writeReport(query, searches)
            yield "sending email"
            await self.emailReport(report)
            yield "email sent, all done"
            yield report.markdwonReport



