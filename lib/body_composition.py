from math import floor

# "Reverse engineered from the Mi Body Composition Scale's library, could also
# be used on some other scales such as iHealth"
#  - Jason F <jason@prototux.net>
# Originally licensed under the Apache License.


class BodyComposition:
    def __init__(self, weight, height, age, sex, impedance):
        self.weight = weight
        self.height = height
        self.age = age
        self.sex = sex
        self.impedance = impedance

        # Check for potential out of boundaries
        if self.height > 220:
            raise Exception("Height is too high (limit: >220cm)")
        elif weight < 10 or weight > 200:
            raise Exception("Weight is either too low or too high (limits: <10kg and >200kg)")
        elif age > 99:
            raise Exception("Age is too high (limit >99 years)")
        elif impedance > 3000:
            raise Exception("Impedance is too high (limit >3000ohm)")

    # Set the value to a boundary if it overflows
    def check_value_overflow(self, value, minimum, maximum):
        if value < minimum:
            return minimum
        elif value > maximum:
            return maximum
        else:
            return value

    # Get LBM coefficient (with impedance)
    def get_LBM_coefficient(self):
        lbm =  (self.height * 9.058 / 100) * (self.height / 100)
        lbm += self.weight * 0.32 + 12.226
        lbm -= self.impedance * 0.0068
        lbm -= self.age * 0.0542
        return lbm

    # Get BMR
    def get_BMR(self):
        if self.sex == 'female':
            bmr = 864.6 + self.weight * 10.2036
            bmr -= self.height * 0.39336
            bmr -= self.age * 6.204
        else:
            bmr = 877.8 + self.weight * 14.916
            bmr -= self.height * 0.726
            bmr -= self.age * 8.976

        # Capping
        if self.sex == 'female' and bmr > 2996:
            bmr = 5000
        elif self.sex == 'male' and bmr > 2322:
            bmr = 5000
        return self.check_value_overflow(bmr, 500, 10000)

    # Get BMR scale
    def get_BMR_scale(self):
        coefficients = {
            'female': {12: 34, 15: 29, 17: 24, 29: 22, 50: 20, 120: 19},
            'male': {12: 36, 15: 30, 17: 26, 29: 23, 50: 21, 120: 20}
        }

        for age, coefficient in coefficients[self.sex].items():
            if self.age < age:
                return [self.weight * coefficient]

    # Get fat percentage
    def get_fat_percentage(self):
        # Set a constant to remove from LBM
        if self.sex == 'female' and self.age <= 49:
            const = 9.25
        elif self.sex == 'female' and self.age > 49:
            const = 7.25
        else:
            const = 0.8

        # Calculate body fat percentage
        LBM = self.get_LBM_coefficient()

        if self.sex == 'male' and self.weight < 61:
            coefficient = 0.98
        elif self.sex == 'female' and self.weight > 60:
            coefficient = 0.96
            if self.height > 160:
                coefficient *= 1.03
        elif self.sex == 'female' and self.weight < 50:
            coefficient = 1.02
            if self.height > 160:
                coefficient *= 1.03
        else:
            coefficient = 1.0
        fatPercentage = (1.0 - (((LBM - const) * coefficient) / self.weight)) * 100

        # Capping body fat percentage
        if fatPercentage > 63:
            fatPercentage = 75
        return self.check_value_overflow(fatPercentage, 5, 75)

    # Get fat percentage scale
    def get_fat_percentage_scale(self):
        # The included tables where quite strange, maybe bogus, replaced them with better ones...
        scales = [
            {'min': 0, 'max': 20, 'female': [18, 23, 30, 35], 'male': [8, 14, 21, 25]},
            {'min': 21, 'max': 25, 'female': [19, 24, 30, 35], 'male': [10, 15, 22, 26]},
            {'min': 26, 'max': 30, 'female': [20, 25, 31, 36], 'male': [11, 16, 21, 27]},
            {'min': 31, 'max': 35, 'female': [21, 26, 33, 36], 'male': [13, 17, 25, 28]},
            {'min': 46, 'max': 40, 'female': [22, 27, 34, 37], 'male': [15, 20, 26, 29]},
            {'min': 41, 'max': 45, 'female': [23, 28, 35, 38], 'male': [16, 22, 27, 30]},
            {'min': 46, 'max': 50, 'female': [24, 30, 36, 38], 'male': [17, 23, 29, 31]},
            {'min': 51, 'max': 55, 'female': [26, 31, 36, 39], 'male': [19, 25, 30, 33]},
            {'min': 56, 'max': 100, 'female': [27, 32, 37, 40], 'male': [21, 26, 31, 34]},
        ]

        for scale in scales:
            if self.age >= scale['min'] and self.age <= scale['max']:
                return scale[self.sex]

    # Get water percentage
    def get_water_percentage(self):
        waterPercentage = (100 - self.get_fat_percentage()) * 0.7

        if (waterPercentage <= 50):
            coefficient = 1.02
        else:
            coefficient = 0.98

        # Capping water percentage
        if waterPercentage * coefficient >= 65:
            waterPercentage = 75
        return self.check_value_overflow(waterPercentage * coefficient, 35, 75)

    # Get water percentage scale
    def get_water_percentage_scale(self):
        return [53, 67]

    # Get bone mass
    def get_bone_mass(self):
        if self.sex == 'female':
            base = 0.245691014
        else:
            base = 0.18016894

        boneMass = (base - (self.get_LBM_coefficient() * 0.05158)) * -1

        if boneMass > 2.2:
            boneMass += 0.1
        else:
            boneMass -= 0.1

        # Capping boneMass
        if self.sex == 'female' and boneMass > 5.1:
            boneMass = 8
        elif self.sex == 'male' and boneMass > 5.2:
            boneMass = 8
        return self.check_value_overflow(boneMass, 0.5, 8)

    # Get bone mass scale
    def get_bone_mass_scale(self):
        scales = [
            {'female': {'min': 60, 'optimal': 2.5}, 'male': {'min': 75, 'optimal': 3.2}},
            {'female': {'min': 45, 'optimal': 2.2}, 'male': {'min': 69, 'optimal': 2.9}},
            {'female': {'min': 0, 'optimal': 1.8}, 'male': {'min': 0, 'optimal': 2.5}}
        ]

        for scale in scales:
            if self.weight >= scale[self.sex]['min']:
                return [scale[self.sex]['optimal']-1, scale[self.sex]['optimal']+1]

    # Get muscle mass
    def get_muscle_mass(self):
        muscleMass = self.weight - ((self.get_fat_percentage() * 0.01) * self.weight) - self.get_bone_mass()

        # Capping muscle mass
        if self.sex == 'female' and muscleMass >= 84:
            muscleMass = 120
        elif self.sex == 'male' and muscleMass >= 93.5:
            muscleMass = 120

        return self.check_value_overflow(muscleMass, 10, 120)

    # Get muscle mass scale
    def get_muscle_mass_scale(self):
        scales = [
            {'min': 170, 'female': [36.5, 42.5], 'male': [49.5, 59.4]},
            {'min': 160, 'female': [32.9, 37.5], 'male': [44.0, 52.4]},
            {'min': 0, 'female': [29.1, 34.7], 'male': [38.5, 46.5]}
        ]

        for scale in scales:
            if self.height >= scale['min']:
                return scale[self.sex]

    # Get Visceral Fat
    def get_visceral_fat(self):
        if self.sex == 'female':
            if self.weight > (13 - (self.height * 0.5)) * -1:
                subsubcalc = ((self.height * 1.45) + (self.height * 0.1158) * self.height) - 120
                subcalc = self.weight * 500 / subsubcalc
                vfal = (subcalc - 6) + (self.age * 0.07)
            else:
                subcalc = 0.691 + (self.height * -0.0024) + (self.height * -0.0024)
                vfal = (((self.height * 0.027) - (subcalc * self.weight)) * -1) + (self.age * 0.07) - self.age
        else:
            if self.height < self.weight * 1.6:
                subcalc = ((self.height * 0.4) - (self.height * (self.height * 0.0826))) * -1
                vfal = ((self.weight * 305) / (subcalc + 48)) - 2.9 + (self.age * 0.15)
            else:
                subcalc = 0.765 + self.height * -0.0015
                vfal = (((self.height * 0.143) - (self.weight * subcalc)) * -1) + (self.age * 0.15) - 5.0

        return self.check_value_overflow(vfal, 1, 50)

    # Get visceral fat scale
    def get_visceral_fat_scale(self):
        return [10, 15]

    # Get BMI
    def get_BMI(self):
        return self.check_value_overflow(self.weight / ((self.height / 100) * (self.height / 100)), 10, 90)

    # Get BMI scale
    def get_BMI_scale(self):
        # Replaced library's version by mi fit scale, it seems better
        return [18.5, 25, 28, 32]

    # Get ideal weight (just doing a reverse BMI, should be something better)
    def get_ideal_weight(self):
        return self.check_value_overflow((22 * self.height) * self.height / 10000, 5.5, 198)

    # Get ideal weight scale (BMI scale converted to weights)
    def get_ideal_weight_scale(self):
        scale = []
        for bmiScale in self.get_BMI_scale():
            scale.append((bmiScale*self.height)*self.height/10000)
        return scale

    # Get fat mass to ideal (guessing mi fit formula)
    def get_fat_mass_to_ideal(self):
        mass = (self.weight * (self.get_fat_percentage() / 100)) - (self.weight * (self.get_fat_percentage_scale()[2] / 100))
        if mass < 0:
            return {'type': 'to_gain', 'mass': mass*-1}
        else:
            return {'type': 'to_lose', 'mass': mass}

    # Get protetin percentage (warn: guessed formula)
    def get_protein_percentage(self):
        proteinPercentage = 100 - (floor(self.get_fat_percentage() * 100) / 100)
        proteinPercentage -= floor(self.get_water_percentage() * 100) / 100
        proteinPercentage -= floor((self.get_bone_mass() / self.weight * 100) * 100) / 100
        return proteinPercentage

    # Get protein scale (hardcoded in mi fit)
    def get_protein_percentage_scale(self):
        return [16, 20]

    # Get body type (out of nine possible)
    def get_body_type(self):
        if self.get_fat_percentage() > self.get_fat_percentage_scale()[2]:
            factor = 0
        elif self.get_fat_percentage() < self.get_fat_percentage_scale()[1]:
            factor = 2
        else:
            factor = 1

        if self.get_muscle_mass() > self.get_muscle_mass_scale()[1]:
            return 2 + (factor * 3)
        elif self.get_muscle_mass() < self.get_muscle_mass_scale()[0]:
            return (factor * 3)
        else:
            return 1 + (factor * 3)

    # Return body type scale
    def get_body_type_scale(self):
        return ['obese', 'overweight', 'thick-set', 'lack-exerscise', 'balanced', 'balanced-muscular', 'skinny', 'balanced-skinny', 'skinny-muscular']