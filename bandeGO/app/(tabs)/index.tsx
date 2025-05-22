// screens/HomeScreen.tsx (ou onde seu HomeScreen está)
import React, { useState, useCallback } from "react"; // Importar useState e useCallback
import { View, Text } from "react-native"; // Importar View e Text
import ParallaxScrollView from "@/components/ParallaxScrollView";
import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";
import { FoodCard } from "@/components/FoodCard";
import { LocationSelector } from "@/components/ui/locationSelect"; // Seu LocationSelector
import {
  MealItem,
  DayOfWeek,
  restaurantData,
} from "@/components/MockLists/MockMeals"; // Suas interfaces

export default function HomeScreen() {
  const [selectedLocationId, setSelectedLocationId] = useState<string | null>(
    null
  );
  const [selectedDay, setSelectedDay] = useState<DayOfWeek | null>(null);

  // Função para ser passada para LocationSelector para receber a seleção
  const handleLocationAndDaySelection = useCallback(
    (locationId: string | null, day: DayOfWeek | null) => {
      setSelectedLocationId(locationId);
      setSelectedDay(day);
    },
    []
  );

  // Encontrar o menu do dia e local selecionados
  const currentMenu: MealItem[] = React.useMemo(() => {
    if (!selectedLocationId || !selectedDay) {
      return []; // Retorna um array vazio se nada estiver selecionado
    }

    const location = restaurantData.find(
      (loc) => loc.id === selectedLocationId
    );
    if (!location) {
      return [];
    }

    const dailyMenu = location.dailyMenus.find(
      (dm) => dm.dayOfWeek === selectedDay
    );
    return dailyMenu ? dailyMenu.menuItems : [];
  }, [selectedLocationId, selectedDay]); // Depende dos estados selecionados

  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: "#A1CEDC", dark: "#1D3D47" }}
    >
      <ThemedView styleProps="flex w-full flex-col items-center py-8">
        <ThemedText type="title">Bem-vindo!</ThemedText>
        {/* Aqui você pode adicionar um título ou mensagem de boas-vindas */}
      </ThemedView>

      <ThemedView styleProps="flex flex-col w-full items-center justify-center p-4">
        <ThemedText className="text-xl font-bold mb-4">
          Opção de Bandeijão
        </ThemedText>
        {/* Passamos a função de callback para o LocationSelector */}
        <LocationSelector onSelection={handleLocationAndDaySelection} />

        {/* Exibir o menu selecionado */}
        {selectedLocationId && selectedDay && currentMenu.length > 0 ? (
          <ThemedView styleProps="flex flex-col w-full">
            <ThemedText className="text-lg font-semibold mb-4">
              Menu de{" "}
              {restaurantData.find((l) => l.id === selectedLocationId)?.name}{" "}
              para {selectedDay}
            </ThemedText>
            {currentMenu.map((meal, index) => (
              <FoodCard
                key={`${selectedLocationId}-${selectedDay}-${index}`} // Chave única
                title={meal.title}
                description={meal.description}
                notes={meal.notes}
                image={meal.image}
              />
            ))}
          </ThemedView>
        ) : (
          <View className="mt-8 p-4 bg-gray-100 rounded-lg">
            <Text className="text-gray-600 text-center">
              Selecione um local e um dia da semana para ver o menu.
            </Text>
          </View>
        )}
      </ThemedView>
    </ParallaxScrollView>
  );
}
