# SPRINGS
QA-bot, that answer based on user pdf files data.

How to build?
  Nothing special was used to build this project.
  You need only Python and pip installed on your system.
  
Below is a detailed instruction on how to run the program:
1. Install Python from official website
2. Get openai api key in official website - https://openai.com/blog/openai-api
3. Find a .env file in the root directory of this project and add your OpenAI API key:
   GPT_TOKEN="your_openai_api_key"
4. Install dependencies:
  pip install -r requirements.txt
5. Run python code with one argument - path to your pdf file.
   python Bot\main.py "path_to_your_pdf_file"

If everything is set up correctly, the bot will work as follows:
1. Prompt you to enter your query (Please note that the response time may vary depending on the size of the PDF file and the current load on the OpenAI servers. Larger PDF files or higher server loads may result in longer response times. Your patience is appreciated :)")
2. Provide an answer based on the query input and pdf file data.

Here is a graphical model of how the program works

  ![image](https://github.com/eagle218/SPRINGS/assets/113504886/d981ce1b-4d76-400b-be90-a3b9dd6e948d)
