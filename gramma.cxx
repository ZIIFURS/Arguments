#encoding "utf8"

PersonName -> AnyWord<kwtype="Surname">;

Person -> PersonName interp(Person.Surname);
