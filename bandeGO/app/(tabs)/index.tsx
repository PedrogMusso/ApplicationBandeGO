import React, { useState, useCallback, useEffect, useTransition } from "react";
import { View, Text } from "react-native";
import ParallaxScrollView from "@/components/ParallaxScrollView";
import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";
import { FoodCard } from "@/components/FoodCard";
import { LocationSelector } from "@/components/ui/locationSelect";
import {
  MealItem,
  DayOfWeek,
  restaurantData,
} from "@/components/MockLists/MockMeals";
import { Button, ButtonText, ButtonSpinner } from "@/components/ui/button";
import axios from "axios";

export default function HomeScreen() {
  const [selectedLocationId, setSelectedLocationId] = useState<string | null>(
    null
  );
  const [selectedDay, setSelectedDay] = useState<DayOfWeek | null>(null);
  const [count, setCount] = useState<number | null>(0);
  const [isPending, startTransition] = useTransition();

  // Função para ser passada para LocationSelector para receber a seleção
  const handleLocationAndDaySelection = useCallback(
    (locationId: string | null, day: DayOfWeek | null) => {
      setSelectedLocationId(locationId);
      setSelectedDay(day);
      console.log(locationId, day);
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

  //após o usuário confirmar a localização, buscaremos o valor de uma requisição no banco de dados
  const handleLocationConfirmed = useCallback(async () => {
    if (!selectedLocationId) return;

    let data = {
      locationId: selectedLocationId,
    };

    try {
      const response = await axios.get("/contagem", {
        params: data,
      });
      startTransition(() => {
        setCount(response.data.count);
      });
    } catch (error) {
      console.error("Erro ao buscar contagem:", error);
      startTransition(() => {
        setCount(0);
      });
    }
  }, [selectedLocationId]);

  useEffect(() => {
    if (selectedLocationId && selectedDay) {
      handleLocationConfirmed();
    }
  }, [selectedLocationId, selectedDay, handleLocationConfirmed]);

  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: "#A1CEDC", dark: "#1D3D47" }}
    >
      <ThemedView styleProps="flex w-full flex-col items-center py-8">
        <ThemedText type="title">Bem-vindo!</ThemedText>
        <Button
          action="primary"
          variant="solid"
          isDisabled={isPending}
          className="mt-4"
        >
          {isPending ? (
            <ButtonSpinner />
          ) : (
            <ButtonText>Total: {count ?? "N/A"}</ButtonText>
          )}
        </Button>
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
