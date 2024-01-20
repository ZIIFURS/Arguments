#encoding "utf-8"

PersonName -> AnyWord<kwtype="Surname">;
PlaceName -> AnyWord<kwtype="Place">;

Out -> PersonName interp(Out.Surname);
Out -> PlaceName interp(Sight.Place);

