{% macro is_weekend(column_name) %}
    extract(dayofweek from {{ date_column }}) in (1, 7)
{% endmacro %}