-- Given the table schemas below, write a query to print a new pizza recipe
-- that includes the most used 5 ingredients in all the ordered pizzas in the past 6 months.

select id, sum(ing_qty) as total
from (
	select i.id, count(*) as ing_qty
	from PizzaOverflow.pizza p 
	left join PizzaOverflow.orders o on p.id = o.pizza_id 
	left join PizzaOverflow.ingredients i on (p.ingredients = i.id or p.ingredients like concat('%, ',i.id,',%') or p.ingredients like concat(i.id,',%') or p.ingredients like concat('%, ',i.id))
		and (not (o.exclusions = i.id or o.exclusions like concat('%, ',i.id,',%') or o.exclusions like concat(i.id,',%') or o.exclusions like concat('%, ',i.id)) or o.exclusions is null)
	-- this condition leaves all orders out
	where o.order_time > current_timestamp()  - interval 6 month
	group by 1
	union all
	select i.id, count(*) as ing_qty
	from PizzaOverflow.orders o
	left join PizzaOverflow.ingredients i on (o.extras = i.id or o.extras like concat('%, ',i.id,',%') or o.extras like concat(i.id,',%') or o.extras like concat('%, ',i.id))
	where i.id is not null
	-- this condition leaves all orders out
	and o.order_time > current_timestamp()  - interval 6 month
	group by 1) as t
group by 1
order by 2 desc;


-- Help the cook by generating an alphabetically ordered comma separated ingredient list
-- for each ordered pizza and add a 2x in front of any ingredient that is requested as
-- extra and is present in the standard recipe too

select order_id, ordered_pizza_id, replace(GROUP_CONCAT(concat(name,if(total>1,concat(total,'x'),'')) order by name asc),',',', ')
from (
	select ordered_pizza_id, order_id, name, sum(qty) as total 
	from (
		with orders_unique1 as (
			select o.order_id, o.pizza_id, o.exclusions
			, ROW_NUMBER() OVER (partition by o.order_id order by o.pizza_id) as ordered_pizza_id
			from PizzaOverflow.orders o)
		select o.ordered_pizza_id
		, o.order_id
		, i.name
		, count(*) as qty
		from PizzaOverflow.pizza p 
		left join orders_unique1 o on p.id = o.pizza_id 
		left join PizzaOverflow.ingredients i on (p.ingredients = i.id or p.ingredients like concat('%, ',i.id,',%') or p.ingredients like concat(i.id,',%') or p.ingredients like concat('%, ',i.id))
			and (not (o.exclusions = i.id or o.exclusions like concat('%, ',i.id,',%') or o.exclusions like concat(i.id,',%') or o.exclusions like concat('%, ',i.id)) or o.exclusions is null)
		group by 1,2,3
		union all (
		with orders_unique2 as (
			select o.order_id, o.pizza_id, o.extras
			, ROW_NUMBER() OVER (partition by o.order_id order by o.pizza_id) as ordered_pizza_id
			from PizzaOverflow.orders o)
		select o.ordered_pizza_id
		, o.order_id
		, i.name
		, count(*) as qty
		from orders_unique2 o
		left join PizzaOverflow.ingredients i on (o.extras = i.id or o.extras like concat('%, ',i.id,',%') or o.extras like concat(i.id,',%') or o.extras like concat('%, ',i.id))
		where i.id is not null
		group by 1,2,3)
		) as t
	group by 1,2,3) as aux
group by 1,2
order by 1,2;