{{ config(schema='marts') }}
with quote as (
    select * from {{ ref('stg_stock_quotes') }}
),

companies as (
    select * from {{ ref('dim_company') }}
),

joined as (
    select
        -- keys
        q.symbol,
        q.trade_date,
        -- company details
        c.company_name,
        c.sector,
        c.industry,
        c.sector_category,
        -- prices
        q.open_price,
        q.high_price,
        q.low_price,
        q.close_price,
        q.prev_close_price,
        -- performance
        q.price_change,
        q.price_change_pct,
        q.day_direction,
        {{ pct_to_label('q.price_change_pct') }} as performance_label,  -- noqa: TMP,PRS,LT02
        round(q.high_price - q.low_price, 2) as intraday_range,
        round(
            (q.high_price - q.low_price) /
            nullif(q.prev_close_price, 0) * 100, 2
        ) as intraday_range_pct,
        q.ingested_at
    from quote as q
    left join companies as c on q.symbol = c.symbol
)

select * from joined
