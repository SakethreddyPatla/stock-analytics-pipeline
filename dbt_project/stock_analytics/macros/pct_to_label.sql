{% macro pct_to_label(column_name) %}
    case
        when {{ column_name }} >= 3.0 then 'strong up'
        when {{ column_name }} >= 0.5 then 'up'
        when {{ column_name }} <= -3.0 then 'strong down'
        when {{ column_name }} <= -0.5 then 'down'
        else 'flat'
    end 
{% endmacro %}