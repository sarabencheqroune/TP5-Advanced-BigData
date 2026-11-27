-- Test générique : aucune combinaison de colonnes ne doit apparaître deux fois
{% test grain_unique(model, colonnes) %}
select {{ colonnes | join(', ') }}, count(*) as n
from {{ model }}
group by {{ colonnes | join(', ') }}
having count(*) > 1
{% endtest %}
