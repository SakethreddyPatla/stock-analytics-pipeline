with fct as (
    select * from {{ ref('fct_daily_trading') }}
),

aggregated as (
    select
        trade_date,
        sector,
        sector_category,

        -- how many stocks in this sector traded today
        count(distinct symbol) as stock_count,

        -- average performance across sector
        round(avg(price_change_pct), 4) as avg_change_pct,
        round(min(price_change_pct), 4) as min_change_pct,
        round(max(price_change_pct), 4) as max_change_pct,

        -- how many stocks went up vs down
        countif(day_direction = 'up') as stocks_up,
        countif(day_direction = 'down') as stocks_down,
        countif(day_direction = 'flat') as stocks_flat,

        -- sector sentiment: majority up or down?
        case
            when
                countif(day_direction = 'up')
                > countif(day_direction = 'down') then 'bullish'
            when
                countif(day_direction = 'down')
                > countif(day_direction = 'up') then 'bearish'
            else 'neutral'
        end as sector_sentiment,

        -- best and worst performer in sector
        max_by(symbol, price_change_pct) as top_performer,
        min_by(symbol, price_change_pct) as worst_performer

    from fct
    group by trade_date, sector, sector_category
)

select * from aggregated
