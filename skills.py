import re

def extract_skills(text):
    text_lower = text.lower()
    found = []
    for skill, aliases in SKILLS.items():
        for alias in aliases:
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text_lower):
                found.append(skill)
                break
    return found

SKILLS = {
    "python": ["python"],
    "sql": ["sql", "sql server", "tsql", "t-sql"],
    "r": ["r programming", "r language"],
    "sas": ["sas"],
    "scala": ["scala"],
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],

    # Libraries
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "matplotlib": ["matplotlib"],
    "seaborn": ["seaborn"],
    "plotly": ["plotly"],
    "xgboost": ["xgboost"],
    "lightgbm": ["lightgbm"],

    # Databases
    "snowflake": ["snowflake"],
    "bigquery": ["bigquery", "google bigquery"],
    "redshift": ["redshift", "amazon redshift"],
    "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb"],
    "oracle": ["oracle"],
    "duckdb": ["duckdb"],

    # Data Engineering
    "dbt": ["dbt", "data build tool"],
    "airflow": ["airflow", "apache airflow"],
    "dagster": ["dagster"],
    "prefect": ["prefect"],
    "fivetran": ["fivetran"],
    "etl": ["etl"],
    "elt": ["elt"],
    "data pipeline": ["data pipeline", "data pipelines"],
    "data modeling": ["data modeling", "data modelling", "dimensional modeling", "dimensional modelling"],

    # Big Data
    "spark": ["spark", "apache spark"],
    "pyspark": ["pyspark"],
    "kafka": ["kafka", "apache kafka"],
    "hadoop": ["hadoop"],
    "hive": ["hive"],
    "flink": ["flink", "apache flink"],
    "databricks": ["databricks"],
    "delta lake": ["delta lake"],
    "iceberg": ["iceberg", "apache iceberg"],

    # Cloud
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "microsoft fabric": ["microsoft fabric", "fabric"],
    "azure synapse": ["azure synapse", "synapse"],
    "azure data factory": ["azure data factory", "adf"],
    "aws glue": ["aws glue"],
    "aws athena": ["athena", "aws athena"],

    # BI
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "looker": ["looker"],
    "looker studio": ["looker studio", "google data studio", "data studio"],
    "sigma": ["sigma"],
    "qlik": ["qlik", "qlik sense"],
    "thoughtspot": ["thoughtspot"],
    "domo": ["domo"],
    "metabase": ["metabase"],
    "superset": ["superset", "apache superset"],
    "hex": ["hex"],

    # Excel
    "excel": ["excel", "microsoft excel"],
    "power query": ["power query"],
    "power pivot": ["power pivot"],
    "dax": ["dax"],
    "pivot tables": ["pivot table", "pivot tables"],
    "vlookup": ["vlookup"],
    "xlookup": ["xlookup"],
    "index match": ["index match", "index-match"],

    # Dev
    "git": ["git"],
    "github": ["github"],
    "gitlab": ["gitlab"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "jira": ["jira"],

    # Statistics
    "statistics": ["statistics", "statistical analysis"],
    "hypothesis testing": ["hypothesis testing"],
    "regression": ["regression", "linear regression", "logistic regression"],
    "anova": ["anova"],
    "forecasting": ["forecasting"],
    "time series": ["time series", "time-series"],
    "bayesian statistics": ["bayesian statistics", "bayesian analysis"],

    # Product Analytics
    "product analytics": ["product analytics"],
    "funnel analysis": ["funnel analysis"],
    "cohort analysis": ["cohort analysis"],
    "retention analysis": ["retention analysis"],
    "churn analysis": ["churn analysis"],
    "customer analytics": ["customer analytics"],

    # Experimentation
    "a/b testing": ["a/b testing", "ab testing", "split testing"],
    "experimentation": ["experimentation"],
    "causal inference": ["causal inference"],
    "incrementality": ["incrementality"],

    # Marketing Analytics
    "marketing analytics": ["marketing analytics"],
    "web analytics": ["web analytics"],
    "attribution": ["attribution"],
    "marketing mix modeling": ["marketing mix modeling", "mmm"],
    "customer lifetime value": ["customer lifetime value", "clv", "ltv"],
    "roas": ["roas"],
    "cac": ["cac"],

    # ML
    "machine learning": ["machine learning", "ml"],
    "predictive modeling": ["predictive modeling"],
    "classification": ["classification"],
    "clustering": ["clustering"],
    "feature engineering": ["feature engineering"],
    "mlops": ["mlops"],
    "feature store": ["feature store"],

    # AI
    "artificial intelligence": ["artificial intelligence", "ai"],
    "generative ai": ["generative ai", "genai"],
    "llm": ["llm", "large language model", "large language models"],
    "chatgpt": ["chatgpt"],
    "gpt": ["gpt", "gpt-4", "gpt-5"],
    "claude": ["claude"],
    "gemini": ["gemini"],
    "prompt engineering": ["prompt engineering"],
    "rag": ["rag", "retrieval augmented generation"],
    "vector database": ["vector database", "vector databases"],
    "vector search": ["vector search"],
    "embeddings": ["embeddings"],
    "fine tuning": ["fine tuning", "fine-tuning"],
    "ai agents": ["ai agents", "agentic ai", "autonomous agents"],
    "copilot": ["copilot"],

    # Governance
    "data governance": ["data governance"],
    "data quality": ["data quality"],
    "data lineage": ["data lineage"],
    "metadata management": ["metadata management"],
    "master data management": ["master data management", "mdm"],
    "gdpr": ["gdpr"],
    "ccpa": ["ccpa"],

    # Business
    "business intelligence": ["business intelligence", "bi"],
    "dashboarding": ["dashboarding", "dashboard development"],
    "data storytelling": ["data storytelling"],
    "kpi": ["kpi", "kpis", "key performance indicator", "key performance indicators"],
    "stakeholder management": ["stakeholder management"],
    "requirements gathering": ["requirements gathering", "business requirements"]
}