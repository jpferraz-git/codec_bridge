# def numOfUnplacedFruits(self, fruits, baskets):
#     """
#     :type fruits: List[int]
#     :type baskets: List[int]
#     :rtype: int
#     """
#     newList = []
#     for i in range(len(fruits)):
#         for j in range(len(baskets)):
#             j = i
#             if fruits[i] >= baskets[j]:
#                 newList.index(i) = newList.append(fruits[i])
#
#     if fruits == newList:
#         return 0
#
#     return 1
# numOfUnplacedFruits([1,2,3], [4,1,5])

# numero = 121
# a = str(numero)
#
# string_reversa = ""
# for i in range(len(a)):
#     string_reversa += a[len(a) - i+1]


# print(string_reversa)


numero = 121

multiplicador = 1
# while int(numero) / 10 > 0:
#     multiplicador *= 10
#
#     numero_normal_decimal = numero / multiplicador
#
#     primeiro_numero = int(numero * 10)
#
#      #ultimo_numero
#     index_numero = int(numero / 10)
#     ultimo_numero = int((index_numero- int(index_numero)) * 10)
#
#     if (numero / 10 != ultimo_numero):
#         return False
#     numero = int(numero / 10)

#
# return True

def addTwoNumbers(array1, array2):
     array1.reverse()
     array2.reverse()

     if len(array1) >= len(array2): array_length = len(array1)
     else: array_length = len(array2)

     new_array = []
     for i in range(array_length):
          element = array1[i] + array2[i]

          if element >= 10:
               element = element - 10
          new_array.append(element)

     print(new_array.reverse())
     return new_array


addTwoNumbers([1,2], [3,4])
