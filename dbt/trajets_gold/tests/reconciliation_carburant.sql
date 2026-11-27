-- Test singulier : les litres des trajets doivent coller aux relevés des cartes
{{ config(severity='warn') }}  -- règle encore en calibration : signaler sans bloquer
-- (écart de plus de 1 % sur une journée = une ligne retournée = test en échec)
select
    g.jour,
    sum(g.litres)                                     as litres_trajets,
    r.litres_factures,
    round(100 * (sum(g.litres) / r.litres_factures - 1), 2) as ecart_pct
from {{ ref('trajets_jour') }} g
join {{ ref('releves_carburant') }} r on r.jour = g.jour
group by g.jour, r.litres_factures
having abs(sum(g.litres) / r.litres_factures - 1) > 0.01
