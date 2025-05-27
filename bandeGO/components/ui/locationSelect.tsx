// components/ui/locationSelect.tsx
import {
  Actionsheet,
  ActionsheetContent,
  ActionsheetItem,
  ActionsheetItemText,
  ActionsheetDragIndicator,
  ActionsheetDragIndicatorWrapper,
  ActionsheetBackdrop,
  ActionsheetVirtualizedList,
} from "@/components/ui/actionsheet";
import React, { useCallback, useMemo, useState } from "react";
import { TouchableOpacity, Text, View } from "react-native";
import {
  restaurantData,
  Location,
  DayOfWeek,
  DailyMenu,
} from "../MockLists/MockMeals";

// Definir as props que o LocationSelector vai receber
interface LocationSelectorProps {
  onSelection: (
    selectedLocationId: string | null,
    selectedDay: DayOfWeek | null
  ) => void;
}

// Tipo de item para a VirtualizedList de Locais
interface SelectableLocationItem {
  id: string;
  title: string; // Nome do local
}

// Tipo de item para a VirtualizedList de Dias
interface SelectableDayItem {
  day: DayOfWeek;
  title: DayOfWeek; // Nome do dia
}

export function LocationSelector({ onSelection }: LocationSelectorProps) {
  const [showLocationsActionsheet, setShowLocationsActionsheet] =
    useState(false);
  const [showDaysActionsheet, setShowDaysActionsheet] = useState(false);

  const [currentSelectedLocationId, setCurrentSelectedLocationId] = useState<
    string | null
  >(null);
  const [currentSelectedDay, setCurrentSelectedDay] =
    useState<DayOfWeek | null>(null);

  // Dados para a lista de locais
  const locationsData: SelectableLocationItem[] = useMemo(
    () => restaurantData.map((loc) => ({ id: loc.id, title: loc.name })),
    []
  );

  // Dados para a lista de dias do local atualmente selecionado
  const daysData: SelectableDayItem[] = useMemo(() => {
    if (!currentSelectedLocationId) return [];
    const selectedLocation = restaurantData.find(
      (loc) => loc.id === currentSelectedLocationId
    );
    return selectedLocation
      ? selectedLocation.dailyMenus.map((dm) => ({
          day: dm.dayOfWeek,
          title: dm.dayOfWeek,
        }))
      : [];
  }, [currentSelectedLocationId]);

  // Função para abrir a ActionSheet de locais
  const openLocationsSheet = useCallback(() => {
    setShowLocationsActionsheet(true);
    setShowDaysActionsheet(false); // Garante que a de dias esteja fechada
  }, []);

  // Função para fechar qualquer ActionSheet
  const handleClose = useCallback(() => {
    setShowLocationsActionsheet(false);
    setShowDaysActionsheet(false);
  }, []);

  // Handler para selecionar um local
  const handleLocationSelect = useCallback(
    (locationItem: SelectableLocationItem) => {
      setCurrentSelectedLocationId(locationItem.id);
      setCurrentSelectedDay(null); // Resetar dia ao mudar de local
      setShowLocationsActionsheet(false); // Fecha a ActionSheet de locais
      setShowDaysActionsheet(true); // Abre a ActionSheet de dias
    },
    []
  );

  // Handler para selecionar um dia
  const handleDaySelect = useCallback(
    (dayItem: SelectableDayItem) => {
      setCurrentSelectedDay(dayItem.day);
      setShowDaysActionsheet(false); // Fecha a ActionSheet de dias
      // Chama a prop onSelection para comunicar ao componente pai
      onSelection(currentSelectedLocationId, dayItem.day);
    },
    [currentSelectedLocationId, onSelection]
  ); // Depende do local e da função onSelection

  // Componente de Item para a lista de locais
  const LocationListItem = useCallback(
    ({ item }: { item: SelectableLocationItem }) => (
      <ActionsheetItem onPress={() => handleLocationSelect(item)}>
        <ActionsheetItemText>{item.title}</ActionsheetItemText>
      </ActionsheetItem>
    ),
    [handleLocationSelect]
  );

  // Componente de Item para a lista de dias
  const DayListItem = useCallback(
    ({ item }: { item: SelectableDayItem }) => (
      <ActionsheetItem onPress={() => handleDaySelect(item)}>
        <ActionsheetItemText>{item.title}</ActionsheetItemText>
      </ActionsheetItem>
    ),
    [handleDaySelect]
  );

  // Funções getItem e getItemCount (genéricas para VirtualizedList)
  const getItem = useCallback(
    (_data: any[], index: number) => _data[index],
    []
  ); // Pode ser mais genérico ou tipado
  const getItemCount = useCallback((_data: any[]) => _data.length, []); // Pode ser mais genérico ou tipado

  return (
    <View className="w-full items-center p-4">
      <TouchableOpacity
        onPress={openLocationsSheet}
        className="p-3 bg-[#FF8A37] rounded-md"
      >
        <Text className="text-white text-base">
          {currentSelectedLocationId && currentSelectedDay
            ? `Menu: ${
                restaurantData.find((l) => l.id === currentSelectedLocationId)
                  ?.name
              } (${currentSelectedDay})`
            : "Selecionar Local e Dia"}
        </Text>
      </TouchableOpacity>

      {/* Actionsheet para Seleção de Locais */}
      <Actionsheet
        isOpen={showLocationsActionsheet}
        onClose={handleClose}
        snapPoints={[50]}
      >
        <ActionsheetBackdrop />
        <ActionsheetContent>
          <ActionsheetDragIndicatorWrapper>
            <ActionsheetDragIndicator />
          </ActionsheetDragIndicatorWrapper>
          <Text className="text-xl font-bold mb-4">Escolha um Local</Text>
          <ActionsheetVirtualizedList
            data={locationsData}
            initialNumToRender={5}
            renderItem={({ item }: { item: any }) => (
              <LocationListItem item={item as SelectableLocationItem} />
            )} // Tipagem ajustada
            keyExtractor={(item: any) =>
              (item as SelectableLocationItem).id.toString()
            } // Tipagem ajustada
            getItemCount={getItemCount}
            getItem={getItem}
          />
        </ActionsheetContent>
      </Actionsheet>

      {/* Actionsheet para Seleção de Dias (apenas se um local estiver selecionado) */}
      {currentSelectedLocationId && (
        <Actionsheet
          isOpen={showDaysActionsheet}
          onClose={handleClose}
          snapPoints={[50]}
        >
          <ActionsheetBackdrop />
          <ActionsheetContent>
            <ActionsheetDragIndicatorWrapper>
              <ActionsheetDragIndicator />
            </ActionsheetDragIndicatorWrapper>
            <Text className="text-xl font-bold mb-4">
              Escolha o Dia da Semana
            </Text>
            <ActionsheetVirtualizedList
              data={daysData}
              initialNumToRender={5}
              renderItem={({ item }: { item: any }) => (
                <DayListItem item={item as SelectableDayItem} />
              )} // Tipagem ajustada
              keyExtractor={(item: any) => (item as SelectableDayItem).day} // DayOfWeek já é string
              getItemCount={getItemCount}
              getItem={getItem}
            />
          </ActionsheetContent>
        </Actionsheet>
      )}
    </View>
  );
}
