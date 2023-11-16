{% macro gcd_distance(lat1, lon1, lat2, lon2) %}
        ACOS(
            SIN(ACOS(-1) * {{ lat1 }}/180) * SIN(ACOS(-1) * {{ lat2 }}/180)
            + COS(ACOS(-1) * {{ lat1 }}/180) * COS(ACOS(-1) * {{ lat2 }}/180)
            * COS((ACOS(-1) * {{ lon1 }}/180) - (ACOS(-1) * {{ lon2 }}/180))
        ) * 6371.0
{% endmacro %}