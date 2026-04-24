with tickers as (
    select * from {{ ref('tickers') }}
)

select
    symbol,
    company_name,
    sector,
    industry,
    case sector
        when 'Technology' then 'Growth'
        when 'Healthcare' then 'Defensive'
        when 'Finance' then 'Cyclical'
        when 'Energy' then 'Cyclical'
        when 'Consumer' then 'Defensive'
        else 'Other'
    end as sector_category
from tickers
