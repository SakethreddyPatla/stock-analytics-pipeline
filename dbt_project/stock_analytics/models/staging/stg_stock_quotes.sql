{{ config(schema='staging') }}
with source as (
    select * from {{ source('raw', 'stock_quotes') }}
),

cleaned as (
    select
        -- identifiers
        upper(trim(symbol))                    as symbol,

        -- dates
        cast(date as date)                     as trade_date,

        -- prices (round to 2 decimal places)
        round(cast(open  as numeric), 2)       as open_price,
        round(cast(high  as numeric), 2)       as high_price,
        round(cast(low   as numeric), 2)       as low_price,
        round(cast(close as numeric), 2)       as close_price,
        round(cast(prev_close as numeric), 2)  as prev_close_price,

        -- performance metrics
        round(cast(change     as numeric), 4)  as price_change,
        round(cast(change_pct as numeric), 4)  as price_change_pct,

        -- determine if it was a good or bad day
        case
            when cast(change_pct as numeric) > 0  then 'up'
            when cast(change_pct as numeric) < 0  then 'down'
            else 'flat'
        end                                    as day_direction,

        -- metadata
        cast(ingested_at as timestamp)         as ingested_at

    from source
    where symbol is not null
      and date  is not null
      and close is not null
)

select * from cleaned