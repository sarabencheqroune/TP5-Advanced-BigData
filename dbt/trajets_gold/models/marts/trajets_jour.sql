{{ config(
    materialized='incremental',
    unique_key=['jour', 'ville', 'type_route'],
    incremental_strategy='merge',
    on_schema_change='fail',
    properties={'partitioning': "ARRAY['month(jour)']"}
) }}

with trajets as (
    select * from {{ ref('stg_trajets') }}

    {% if is_incremental() %}
    where jour >= date '{{ var("jour") }}' - interval '2' day
    {% endif %}
)

select
    t.jour,
    t.ville,
    v.region,
    t.type_route,
    count(*) as nb_trajets,
    count(distinct t.voiture_id) as nb_voitures,
    cast(sum(t.distance_km) as decimal(12, 1)) as km,
    cast(sum(t.carburant_l) as decimal(12, 2)) as litres,
    cast(
        sum(t.carburant_l) * 100 / sum(t.distance_km)
        as decimal(6, 2)
    ) as conso_l100
from trajets t
join {{ ref('villes') }} v on v.ville = t.ville
group by 1, 2, 3, 4