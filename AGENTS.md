# Paper Finder AI Instructions

- The project implements a system that scans websites and blogs such as arxiv, Google DeepMind Blog, Anthropic Blog, etc. for new papers that are interesting from a Machine Learning / AI / Optimization perspective. It then uses a language model to read the paper and summarize the contents into a synopsis. The summaries are then combined into a PDF that gets emailed to me at a prescribed time.
- There should be a file that contains the list of all websites that the bot scrapes.
- The language model should use AWS Bedrock for the LLM integration.
- There should be a configuration file that defines the topics and number of papers to return.
- I want to open the possibility for Discord integrations as well.
- There should be a robust CI/CD (GitHub) pipeline which performs various tests the ensure project stability and quality.
- Ideally I would host the service on AWS.
- Since the bot should scrape both papers and blogs, I want links to be included in the return. If links are from arxiv then please use the HTML5 version.
