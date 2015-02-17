//
// Pixie C++ typer
//
// This code (when compiled) will emit EDN data for a given C++ type. This includes C functions
// So calling this:
// PixieChecker::DumpType<typeof(atof)>()
// will emit this in the compiled program:
// {:type :function :arity 1 :returns {:type :float :size 8} :arguments [{:type :pointer :of-type {:type :int :size 1 :signed? true}}  ]}

#include <iostream>
#include "boost/type_traits.hpp"

namespace PixieChecker {

template<typename T>
std::string GetType();

template<class T>
struct GenericChecker;

template < typename T > std::string to_string( const T& n )
{
    std::ostringstream stm ;
    stm << n ;
    return stm.str() ;
}
    

// Function Checker
template <int Arity, class T>
struct FunctionTyper
{
    static std::string getType()
    {
        return "{:type :function :arity :unknown}";
    }
};

template<class T>
struct FunctionTyper<0, T>
{
    static std::string getType()
    {
        return "{:type :function :arity 0 :returns " +
        GetType<typename boost::function_traits<T>::result_type>() +
        " :arguments []}";

    }
};


    template<class T>
    struct FunctionTyper<1, T>
    {
        static std::string getType()
        {
            return "{:type :function :arity 1 :returns " +
            GetType<typename boost::function_traits<T>::result_type>() +
            " :arguments [" +
            GetType<typename boost::function_traits<T>::arg1_type>() + " " +
            " ]}";
        }
    };

    template<class T>
    struct FunctionTyper<2, T>
    {
        static std::string getType()
        {
            return "{:type :function :arity 2 :returns " +
            GetType<typename boost::function_traits<T>::result_type>() +
            " :arguments [" +
            GetType<typename boost::function_traits<T>::arg1_type>() + " " +
            GetType<typename boost::function_traits<T>::arg2_type>() + " " +

            " ]}";
        }
    };


    template<class T>
    struct FunctionTyper<3, T>
    {
        static std::string getType()
        {
            return "{:type :function :arity 3 :returns " +
            GetType<typename boost::function_traits<T>::result_type>() +
            " :arguments [" +
            GetType<typename boost::function_traits<T>::arg1_type>() + " " +
            GetType<typename boost::function_traits<T>::arg2_type>() + " " +
            GetType<typename boost::function_traits<T>::arg3_type>() + " " +
            " ]}";
        }
    };
    
    template<class T>
    struct FunctionTyper<4, T>
    {
        static std::string getType()
        {
            return "{:type :function :arity 4 :returns " +
            GetType<typename boost::function_traits<T>::result_type>() +
            " :arguments [" +
            GetType<typename boost::function_traits<T>::arg1_type>() + " " +
            GetType<typename boost::function_traits<T>::arg2_type>() + " " +
            GetType<typename boost::function_traits<T>::arg3_type>() + " " +
            GetType<typename boost::function_traits<T>::arg4_type>() + " " +
            " ]}";
        }
    };
    

// End Function Typer

// Is Enum
    template<class P, class T>
    struct GenericCheckerIsEnum
    {
        static std::string getType()
        {
            return "Shouldn't happen in enum checker";
        }
    };

    template<class T>
    struct GenericCheckerIsEnum<boost::true_type, T>
    {
        static std::string getType()
        {
          return GetType<int>();
        }
    };

    template<class T>
    struct GenericCheckerIsEnum<boost::false_type, T>
    {
        static std::string getType()
        {
            return "{:type :unknown}";
        }
    };
// End Is Enum



// Is Void
    template<class P, class T>
    struct GenericCheckerIsVoid
    {
        static std::string getType()
        {
            return "Shouldn't happen in void checker";
        }
    };

    template<class T>
    struct GenericCheckerIsVoid<boost::true_type, T>
    {
        static std::string getType()
        {
            return "{:type :void}";
        }
    };

    template<class T>
    struct GenericCheckerIsVoid<boost::false_type, T>
    {
        static std::string getType()
        {
            return  GenericCheckerIsEnum<typename boost::is_enum<T>::type, T>::getType();
        }
    };
// End Is Void

// Is Pointer

template<class ISInt, class T>
struct GenericCheckerIsPointer
{
    static std::string getType()
    {
        return "Shouldn't happen in pointer checker";
    }
};

template<class T>
struct GenericCheckerIsPointer<boost::true_type, T>
{
    static std::string getType()
    {
        return "{:type :pointer :of-type " + GetType<typename boost::remove_pointer<T>::type>() + "}";
    }
};

template<class T>
struct GenericCheckerIsPointer<boost::false_type, T>
{
    static std::string getType()
    {
        return GenericCheckerIsVoid<typename boost::is_void<T>::type, T>::getType();
    }
};


// End Is Pointer



// Is Function

template<class ISInt, class T>
struct GenericCheckerIsFunction
{
    static std::string getType()
    {
        return "Shouldn't happen in function checker";
    }
};

template<class T>
struct GenericCheckerIsFunction<boost::true_type, T>
{
    static std::string getType()
    {
        return FunctionTyper<boost::function_traits<T>::arity, T>::getType();
    }
};

template<class T>
struct GenericCheckerIsFunction<boost::false_type, T>
{
    static std::string getType()
    {
        return GenericCheckerIsPointer<typename boost::is_pointer<T>::type, T>::getType();
    }
};

// End Is Function


// Is Float

template<class ISInt, class T>
struct GenericCheckerIsFloat
{
    static std::string getType()
    {
        throw 42;
    }
};

template<class T>
struct GenericCheckerIsFloat<boost::true_type, T>
{
    static std::string getType()
    {
        return "{:type :float :size " + to_string(sizeof(T)) + "}";
    }
};

template<class T>
struct GenericCheckerIsFloat<boost::false_type, T>
{
    static std::string getType()
    {
        return GenericCheckerIsFunction<typename boost::is_function<T>::type, T>::getType();
    }
};

// End is Float

// IsInt

template<class ISInt, class T>
struct GenericCheckerIsInt
{
    static std::string getType()
    {
        return "Shouldn't happen";
    }
};

template<class T>
struct GenericCheckerIsInt<boost::true_type, T>
{
    static std::string getType()
    {
        return "{:type :int :size " + to_string(sizeof(T)) +
        " :signed? " + (boost::is_signed<T>::value ? "true" : "false") +
        "}";
    }
};

template<class T>
struct GenericCheckerIsInt<boost::false_type, T>
{
    static std::string getType()
    {
        return GenericCheckerIsFloat<typename boost::is_float<T>::type, T>::getType();
    }
};

// End is Int

// Generic Typer
template<typename T>
std::string GetType()
{
    return GenericCheckerIsInt<typename boost::is_integral<T>::type, T>::getType();
}

// End Generic Typer

template<typename T>
void DumpValue(T t)
{
  std::cout << GetType<T>() << std::endl;
}

template<typename T>
void DumpType()
{
  std::cout << GetType<T>() << std::endl;
}

}
