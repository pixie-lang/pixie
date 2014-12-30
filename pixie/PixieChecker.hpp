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

template<class T>
struct GenericChecker;



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
        GenericChecker<typename boost::function_traits<T>::result_type>::getType() +
        " :arguments []}";
        
    }
};


    template<class T>
    struct FunctionTyper<1, T>
    {
        static std::string getType()
        {
            return "{:type :function :arity 1 :returns " +
            GenericChecker<typename boost::function_traits<T>::result_type>::getType() +
            " :arguments [" +
            GenericChecker<typename boost::function_traits<T>::arg1_type>::getType() + " " +
            " ]}";
        }
    };
    
    template<class T>
    struct FunctionTyper<2, T>
    {
        static std::string getType()
        {
            return "{:type :function :arity 2 :returns " +
            GenericChecker<typename boost::function_traits<T>::result_type>::getType() +
            " :arguments [" +
            GenericChecker<typename boost::function_traits<T>::arg1_type>::getType() + " " +
            GenericChecker<typename boost::function_traits<T>::arg2_type>::getType() + " " +
            
            " ]}";
        }
    };
    
    
    template<class T>
    struct FunctionTyper<3, T>
    {
        static std::string getType()
        {
            return "{:type :function :arity 3 :returns " +
            GenericChecker<typename boost::function_traits<T>::result_type>::getType() +
            " :arguments [" +
            GenericChecker<typename boost::function_traits<T>::arg1_type>::getType() + " " +
            GenericChecker<typename boost::function_traits<T>::arg2_type>::getType() + " " +
            GenericChecker<typename boost::function_traits<T>::arg3_type>::getType() + " " +
            " ]}";
        }
    };

// End Function Typer
    
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
            return "{:type :unknown}";
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
        return "{:type :pointer :of-type " + GenericChecker<typename boost::remove_pointer<T>::type>::getType() + "}";
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
        return "{:type :float :size " + std::to_string(sizeof(T)) + "}";
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
        return "{:type :int :size " + std::to_string(sizeof(T)) +
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
template<class T>
struct GenericChecker
{
    static std::string getType()
    {
        return GenericCheckerIsInt<typename boost::is_integral<T>::type, T>::getType();
    }
};

// End Generic Typer
    
template<typename T>
void DumpValue(T t)
{
    std::cout << GenericChecker<T>::getType() << std::endl;
}
    
template<typename T>
void DumpType()
{
    std::cout << GenericChecker<T>::getType() << std::endl;
}

}


