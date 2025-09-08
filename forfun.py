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

if int(numero) / 10 > 0:
     pass

def divisor(numero):
    divisor = 0

    while int(numero) / 10 > 0:
        divisor *= 10

    return divisor


    # numero_normal_decimal = numero / multiplicador
    #
    # primeiro_numero = int(numero * 10)
    #
    #  #ultimo_numero
    # index_numero = int(numero / 10)
    # ultimo_numero = int((index_numero- int(index_numero)) * 10)
    #
    # if (numero / 10 != ultimo_numero):
    #     return False
    # numero = int(numero / 10)

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


def aaa():
    nums = [2,7,9,11]
    target = 18
    nums_set = sorted(set(nums))
    target_index = []
    i = 0
    j = len(nums) - 1

    while True:
        if nums_set[i] + nums_set[j] == target:
            target_index.append([i + 1, j])
            print(target_index)
            return target_index

        elif nums[i] + nums[j] < target:
            i += 1
        elif nums[i] + nums[j] > target:
            j -= 1
# addTwoNumbers([1,2], [3,4])
aaa()