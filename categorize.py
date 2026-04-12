class Categorizer:
    def classify_commune(self, commune):
        """
        تصنيف البلدية حسب المنطقة الحرارية الشتوية
        إذا لم توجد قيمة، يرجع 'Inconnue'
        """
        return commune.get("thermal_zone_winter", "Inconnue")