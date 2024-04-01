
# News of the Day

Suggest only limited amount of news carefully selected for you so that you
won't waste your time keep checking news across multiple news sources and
read many similar articles.

This is a toy project to learn new skills / technologies or system designs.

```mermaid
flowchart LR
    A[Lambda\nscheduled run] -->|Fetch| B[News API]
    A -->|Save|D[S3]
    E[AWS Redshift Severless] <-- copy --> D
    I[dbt\nscheduled on lambda] --> |Transform data| E
    E --> I
    F[User] -- Explore data --> E
    G[Streamlit] -- Visualise data --> E
    H[Redshift ML] -. Use data for ML training .-> E
    H -.-> |Save model|S3
```
